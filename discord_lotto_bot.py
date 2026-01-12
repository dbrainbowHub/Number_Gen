import discord
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import subprocess
import logging
from glob import glob
import pandas as pd
import asyncio
import pytz
from lotto_analyzer import check_latest_round_performance, generate_performance_report

# 파일로 로그 남기기
logging.basicConfig(
    filename='discord_lotto_bot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# 1. 디스코드 봇 토큰과 채널 ID 입력 (.env 파일 사용)
def load_env_file():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        pass
    return env_vars

env_vars = load_env_file()
TOKEN = env_vars.get('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(env_vars.get('DISCORD_CHANNEL_ID', '0'))  # num_gen 채널

# 2. lotto_result.txt에서 최신 결과 블록만 읽는 함수
def get_latest_lotto_result():
    if not os.path.exists('lotto_result.txt'):
        return '추천번호 결과 파일이 없습니다.'
    with open('lotto_result.txt', encoding='utf-8') as f:
        lines = f.read().strip().split('\n')
    # 최근 블록 추출
    idxs = [i for i, line in enumerate(lines) if '번째 추천 번호에요~' in line]
    if not idxs:
        return '\n'.join(lines[-17:])
    last_idx = idxs[-1]
    block = lines[last_idx:]
    if len(block) < 5:
        return '\n'.join(block)
    title = block[0]
    round_line = block[1]
    numbers = block[2:-1]
    footer = block[-1]
    msg = f"{title}\n{round_line}\n" + "\n".join(numbers) + "\n" + footer
    return msg

# 3. 디스코드 클라이언트 정의
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.scheduler = None
        self.channel = None
        self.is_running = False

    async def setup_hook(self):
        # 스케줄러 설정
        self.scheduler = AsyncIOScheduler()
        # 한국 시간대 설정
        seoul_tz = pytz.timezone('Asia/Seoul')
        
        # 매주 토요일 23:00에 자동 업데이트
        self.scheduler.add_job(
            self.scheduled_update,
            'cron',
            day_of_week='sat',
            hour=23,
            minute=0,
            timezone=seoul_tz,
            id='lotto_update'
        )
        
        # 매일 00:00에 스케줄러 상태 체크
        self.scheduler.add_job(
            self.check_scheduler_status,
            'cron',
            hour=0,
            minute=0,
            timezone=seoul_tz,
            id='status_check'
        )

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        logging.info(f'봇이 시작되었습니다: {self.user}')
        
        # 채널 설정 - 다시 시도
        self.channel = None
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.id == CHANNEL_ID:
                    self.channel = channel
                    break
            if self.channel:
                break
                
        if not self.channel:
            # 채널 ID로 직접 접근 시도
            try:
                self.channel = await self.fetch_channel(CHANNEL_ID)
            except Exception as e:
                logging.error(f'채널을 찾을 수 없습니다: {CHANNEL_ID}, 에러: {e}')
                # 모든 채널 ID 로깅
                for guild in self.guilds:
                    logging.info(f'서버 {guild.name}의 채널들:')
                    for channel in guild.channels:
                        logging.info(f'  - {channel.name}: {channel.id}')
                return
            
        # 스케줄러 시작
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logging.info('스케줄러가 시작되었습니다.')
            try:
                await self.channel.send('🎲 당첨번호생성 봇이 시작되었습니다. 매주 토요일 23:00에 자동으로 업데이트됩니다.')
            except Exception as e:
                logging.error(f'시작 메시지 전송 실패: {e}')

    async def check_scheduler_status(self):
        if not self.is_running:
            logging.warning('스케줄러가 중지되었습니다. 재시작을 시도합니다.')
            self.scheduler.start()
            self.is_running = True
            if self.channel:
                try:
                    await self.channel.send('⚠️ 스케줄러가 재시작되었습니다.')
                except Exception as e:
                    logging.error(f'재시작 메시지 전송 실패: {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return
            
        logging.info(f'메시지 수신: {message.content} from {message.author}')
        
        if message.content == '!num':
            # lotto_generator.py 실행 (추천번호 즉시 추출)
            try:
                result = subprocess.run(['python3', 'lotto_generator.py'], 
                                      capture_output=True, text=True, check=True)
                logging.info(f'lotto_generator.py 실행 성공: {result.stdout}')
            except subprocess.CalledProcessError as e:
                logging.error(f'추천번호 생성 중 오류 발생: {e.stderr}')
                await message.channel.send(f'추천번호 생성 중 오류 발생: {e.stderr}')
                return
            except Exception as e:
                logging.error(f'추천번호 생성 중 예상치 못한 오류: {e}')
                await message.channel.send(f'추천번호 생성 중 오류 발생: {e}')
                return
                
            result_text = get_latest_lotto_result()
            await message.channel.send(f'```{result_text}```')
            
        elif message.content == '!update':
            await self.run_update_and_send(message.channel)
            
        elif message.content == '!status':
            status = "실행 중" if self.is_running else "중지됨"
            next_run = None
            if self.is_running and self.scheduler.get_job('lotto_update'):
                next_run = self.scheduler.get_job('lotto_update').next_run_time
            await message.channel.send(f'봇 상태: {status}\n다음 실행 예정: {next_run}')
            
        elif message.content == '!anal':
            try:
                # 디버깅 정보 추가
                import os
                current_dir = os.getcwd()
                result_file_exists = os.path.exists('lotto_result.txt')
                lotto_files = glob('lotto_*.csv')
                
                logging.info(f'분석 명령 실행 - 현재 디렉토리: {current_dir}')
                logging.info(f'lotto_result.txt 존재: {result_file_exists}')
                logging.info(f'로또 파일들: {lotto_files}')
                
                report = generate_performance_report()
                await message.channel.send(f'```{report}```')
            except Exception as e:
                logging.error(f'성과 분석 중 오류: {e}')
                await message.channel.send(f'성과 분석 중 오류가 발생했습니다: {e}')
                
        elif message.content == '!help':
            help_text = """
🎲 **당첨번호 생성기 명령어**

**기본 명령어:**
• `!num` - 새로운 추천번호 생성 (15개 조합)
• `!update` - 최신 당첨번호 수동 업데이트
• `!status` - 봇 상태 및 다음 자동 업데이트 시간 확인

**분석 명령어:**
• `!anal` - 전체 추천번호 성과 분석 리포트
• `!help` - 이 도움말 표시
• `!test` - 봇 작동 상태 테스트

**자동 기능:**
• 매주 토요일 23:00에 자동으로 최신 당첨번호 확인 및 추천번호 생성
• 추천번호 적중률 자동 분석 및 알림
            """
            await message.channel.send(help_text)
            
        elif message.content == '!test':
            await message.channel.send('봇이 정상 작동 중입니다!')

    async def scheduled_update(self):
        logging.info('스케줄된 업데이트가 시작되었습니다.')
        if not self.channel:
            logging.error('채널을 찾을 수 없습니다.')
            return
            
        try:
            await self.run_update_and_send(self.channel, is_scheduled=True)
            logging.info('스케줄된 업데이트가 완료되었습니다.')
        except Exception as e:
            logging.error(f'스케줄된 업데이트 중 오류 발생: {e}')
            try:
                await self.channel.send(f'⚠️ 자동 업데이트 중 오류가 발생했습니다: {e}')
            except Exception as send_error:
                logging.error(f'에러 메시지 전송 실패: {send_error}')

    async def run_update_and_send(self, channel, is_scheduled=False):
        try:
            proc = await asyncio.create_subprocess_exec(
                'python3', 'update_lotto.py',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                await channel.send('업데이트가 1분 내에 끝나지 않았습니다.')
                return
                
            output = (stdout + stderr).decode().strip()
            if proc.returncode == 0:
                # [수정] update_lotto.py의 영어 출력 메시지에 맞춰 조건문 변경
                if 'already exists' in output:
                    msg = '현재는 이게 최신이에요!\n'
                    
                    # 수동 업데이트도 전체 분석 포함
                    # 2. 누적된 추천 번호 중 1등 당첨번호와 일치 여부 알림
                    try:
                        from lotto_analyzer import generate_performance_report
                        full_report = generate_performance_report()
                        
                        # 1등 당첨번호 발견 부분만 추출
                        if "🎊 **1등 당첨번호 발견!**" in full_report:
                            lines = full_report.split('\n')
                            jackpot_section = []
                            in_jackpot_section = False
                            for line in lines:
                                if "🎊 **1등 당첨번호 발견!**" in line:
                                    in_jackpot_section = True
                                    jackpot_section.append(line)
                                elif in_jackpot_section:
                                    if line.strip() == "" and jackpot_section:
                                        break
                                    jackpot_section.append(line)
                            
                            if jackpot_section:
                                msg += '\n🎊 **축하합니다! 1등 당첨번호 발견!**\n'
                                msg += '\n'.join(jackpot_section[1:]) + '\n'  # 첫 줄 제외하고 추가
                        else:
                            msg += '\n📝 누적 추천번호 중 1등 당첨번호는 아직 없습니다.\n'
                    except Exception as e:
                        logging.error(f'1등 당첨번호 확인 중 오류: {e}')
                        msg += f'\n1등 당첨번호 확인 중 오류가 발생했습니다: {e}\n'
                    
                    # 3. 누적된 추천번호 성과 분석 (이전 추천번호 적중률)
                    try:
                        performance = check_latest_round_performance()
                        if performance:
                            msg += '\n📊 최신 추천번호 성과 분석:\n'
                            msg += f"✅ {performance['recommendation_no']:02d}번째 추천 → {performance['target_round']}회차 결과\n"
                            msg += f"🎯 최대 적중: {performance['max_matches']}개\n"
                            
                            # 3개 이상 적중한 라인들 표시
                            good_lines = [line for line in performance['line_results'] if line['matches'] >= 3]
                            if good_lines:
                                msg += f"🔥 3개 이상 적중 라인:\n"
                                for line in good_lines:
                                    nums_str = ' '.join(map(str, line['numbers']))
                                    msg += f"   {line['set']}세트-{line['line']}: {nums_str} ({line['matches']}개)\n"
                            else:
                                msg += "아쉽게도 3개 이상 적중한 라인은 없었습니다.\n"
                        else:
                            msg += '\n📊 최신 추천번호 성과 분석:\n'
                            msg += "아직 분석할 수 있는 성과 데이터가 없습니다.\n"
                    except Exception as e:
                        logging.error(f'성과 분석 중 오류: {e}')
                        msg += f'\n📊 성과 분석 중 오류가 발생했습니다: {e}\n'
                    
                    # 4. 새로운 추천번호 생성
                    try:
                        result = subprocess.run(['python3', 'lotto_generator.py'], 
                                              capture_output=True, text=True, check=True)
                        msg += '\n🎲 새로운 추천번호도 생성했어요!\n'
                        
                        # 생성된 추천번호 표시
                        result_text = get_latest_lotto_result()
                        msg += f'\n```{result_text}```\n'
                        
                        logging.info('자동 추천번호 생성 완료')
                    except Exception as e:
                        logging.error(f'추천번호 생성 중 오류 발생: {e}')
                        msg += f'\n추천번호 생성 중 오류가 발생했습니다: {e}\n'
                    
                    # 현재 최신 당첨번호 정보만 표시 (새로운 추천번호 생성 없음)
                    msg += '\n📈 오늘 기준 최신 당첨번호에요:\n'
                
                # [수정] 성공 메시지도 영어 출력에 맞춰 변경
                elif 'Successfully updated' in output:
                    msg = '🎉 최신 당첨번호가 업데이트되었습니다!\n'
                    
                    # 2. 누적된 추천 번호 중 1등 당첨번호와 일치 여부 알림
                    try:
                        from lotto_analyzer import generate_performance_report
                        full_report = generate_performance_report()
                        
                        # 1등 당첨번호 발견 부분만 추출
                        if "🎊 **1등 당첨번호 발견!**" in full_report:
                            lines = full_report.split('\n')
                            jackpot_section = []
                            in_jackpot_section = False
                            for line in lines:
                                if "🎊 **1등 당첨번호 발견!**" in line:
                                    in_jackpot_section = True
                                    jackpot_section.append(line)
                                elif in_jackpot_section:
                                    if line.strip() == "" and jackpot_section:
                                        break
                                    jackpot_section.append(line)
                            
                            if jackpot_section:
                                msg += '\n🎊 **축하합니다! 1등 당첨번호 발견!**\n'
                                msg += '\n'.join(jackpot_section[1:]) + '\n'  # 첫 줄 제외하고 추가
                        else:
                            msg += '\n📝 누적 추천번호 중 1등 당첨번호는 아직 없습니다.\n'
                    except Exception as e:
                        logging.error(f'1등 당첨번호 확인 중 오류: {e}')
                        msg += f'\n1등 당첨번호 확인 중 오류가 발생했습니다: {e}\n'
                    
                    # 3. 누적된 추천번호 성과 분석 (이전 추천번호 적중률)
                    try:
                        performance = check_latest_round_performance()
                        if performance:
                            msg += '\n📊 이전 추천번호 성과 분석:\n'
                            msg += f"✅ {performance['recommendation_no']:02d}번째 추천 → {performance['target_round']}회차 결과\n"
                            msg += f"🎯 최대 적중: {performance['max_matches']}개\n"
                            
                            # 3개 이상 적중한 라인들 표시
                            good_lines = [line for line in performance['line_results'] if line['matches'] >= 3]
                            if good_lines:
                                msg += f"🔥 3개 이상 적중 라인:\n"
                                for line in good_lines:
                                    nums_str = ' '.join(map(str, line['numbers']))
                                    msg += f"   {line['set']}세트-{line['line']}: {nums_str} ({line['matches']}개)\n"
                            else:
                                msg += "아쉽게도 3개 이상 적중한 라인은 없었습니다.\n"
                        else:
                            msg += '\n📊 이전 추천번호 성과 분석:\n'
                            msg += "아직 분석할 수 있는 성과 데이터가 없습니다.\n"
                    except Exception as e:
                        logging.error(f'성과 분석 중 오류: {e}')
                        msg += f'\n📊 성과 분석 중 오류가 발생했습니다: {e}\n'
                    
                    # 4. 새로운 추천번호 생성
                    try:
                        result = subprocess.run(['python3', 'lotto_generator.py'], 
                                              capture_output=True, text=True, check=True)
                        msg += '\n🎲 새로운 추천번호도 생성했어요!\n'
                        
                        # 생성된 추천번호 표시
                        result_text = get_latest_lotto_result()
                        msg += f'\n```{result_text}```\n'
                        
                        logging.info('자동 추천번호 생성 완료')
                    except Exception as e:
                        logging.error(f'추천번호 생성 중 오류 발생: {e}')
                        msg += f'\n추천번호 생성 중 오류가 발생했습니다: {e}\n'
                    
                    # 현재 최신 당첨번호 정보만 표시 (새로운 추천번호 생성 없음)
                    msg += '\n📈 오늘 기준 최신 당첨번호에요:\n'
                else:
                    msg = '업데이트 결과:\n' + output + '\n'
                    
                # 최신 당첨번호 추출 (lotto_total.csv 기준)
                try:
                    # [주의] lotto_total.csv만 사용하는 경우를 대비해 예외처리
                    # update_lotto.py는 lotto_total.csv만 갱신하므로, 개별 파일을 찾는 glob 로직이
                    # 최신 번호를 못 가져올 수 있습니다. 이 경우 lotto_total.csv를 직접 읽습니다.
                    target_file = 'lotto_total.csv'
                    if os.path.exists(target_file):
                        df = pd.read_csv(target_file)
                        if not df.empty:
                            last_row = df.iloc[-1]
                            # 컬럼명이 1,2,3,4,5,6 인지 확인
                            try:
                                nums = [str(last_row[str(i)]) for i in range(1,7)]
                                bonus = str(last_row['보너스']) if '보너스' in last_row else ''
                                msg += f"회차: {last_row['회차']}\n날짜: {last_row['추첨일']}\n번호: {' '.join(nums)} + {bonus}"
                            except:
                                # 컬럼명이 다를 경우 예외 처리 (인덱스로 접근 등)
                                pass
                except Exception as e:
                    logging.error(f'당첨번호 추출 중 오류: {e}')
                    msg += f"\n당첨번호 추출 중 오류: {e}"
            else:
                msg = f'당첨번호 데이터 최신화 실패!\n{output}'
        except Exception as e:
            msg = f'당첨번호 데이터 최신화 중 오류 발생: {e}'
            logging.error(f'업데이트 중 오류 발생: {e}')
            
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if is_scheduled:
            msg = f'[{now} 자동업데이트]\n' + msg
        await channel.send(msg)

# 4. 봇 실행
if __name__ == "__main__":
    client = MyClient()
    client.run(TOKEN)