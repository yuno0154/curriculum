import os
import subprocess
import sys
import shutil

def run_command(command, cwd=None):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        for line in process.stdout:
            print(line, end='')
        process.wait()
        return process.returncode
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1

def main():
    print("==========================================")
    print("  가상환경 자동 설정 스크립트 (Python 기반)")
    print("==========================================")

    # 경로 설정
    project_name = "성취기준 추출 프로그램"
    target_root = os.path.join("d:\\project", project_name)
    venv_dir = os.path.join(target_root, ".venv")
    
    print(f"\n[1/4] 대상 경로 확인: {target_root}")
    if not os.path.exists(target_root):
        print("      폴더 생성 중...")
        os.makedirs(target_root, exist_ok=True)

    # 가상환경 생성
    print(f"\n[2/4] 가상환경(.venv) 생성 중... (잠시만 기다려 주세요)")
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    else:
        print("      가상환경이 이미 존재합니다.")

    # Python 실행 파일 경로
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # pip 업그레이드
    print(f"\n[3/4] pip 업그레이드 중...")
    subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # 라이브러리 설치
    print(f"\n[4/4] 라이브러리 설치 중 (requirements.txt)...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(script_dir, "requirements.txt")
    
    if os.path.exists(req_path):
        subprocess.run([venv_python, "-m", "pip", "install", "-r", req_path], check=True)
    else:
        print(f"      오류: {req_path} 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print("\n==========================================")
    print("  설정이 완료되었습니다!")
    print("  이제 모든 PC에서 동일한 환경으로 실행됩니다.")
    print("==========================================")
    input("\n계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()
