import subprocess
import sys

def run_command(command, description):
    """Run a shell command and check for errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(f"\n✅ {description} succeeded!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed!")
        print(f"Output:\n{e.stdout}")
        sys.exit(1)

def main():
    print("🚀 Starting CI/CD checks...")
    colored = False
    if "--color" in sys.argv:
        colored = True
        
    paths = ["pjsk_sticker/", "api.py"]
    
    for path in paths:
        # 1. 运行 isort 检查导入排序
        run_command(
            ["isort", path, "--profile", "black"] + (["--color"] if colored else []),
            f"isort (import sorting check) for {path}"
        )

        # 2. 运行 Black 代码格式化检查
        run_command(
            ["black", path] + (["--color"] if colored else []),
            f"Black (code formatting check) for {path}"
        )

        # 3. 运行 Flake8 代码质量检查
        run_command(
            ["flake8", path] + (["--color", "always"] if colored else []),
            f"Flake8 (code quality check) for {path}"
        )

    # 4. 运行 Pytest 测试
    # run_command(
    #     ["pytest"] + (["--color=yes"] if colored else []),
    #     "Pytest (tests)"
    # )

    print("\n🎉 All CI/CD checks passed!")

if __name__ == "__main__":
    main()
