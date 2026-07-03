'''import argparse,subprocess


def dash1():
    parser = argparse.ArgumentParser(description="calculate X to the power of Y")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("x", type=int, help="the base")
    parser.add_argument("y", type=int, help="the exponent")
    args = parser.parse_args()
    answer = args.x**args.y

    if args.quiet:
        print(answer)
    elif args.verbose:
        print(f"{args.x} to the power {args.y} equals {answer}")
    else:
        print(f"{args.x}^{args.y} == {answer}")



def run_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error ocurred: {e.stderr}"
    except FileNotFoundError:
        return "Error: The command was not found."

command_to_run = ["cmd", "/c", "dir"]
output = run_command(command_to_run)
print(output)
'''