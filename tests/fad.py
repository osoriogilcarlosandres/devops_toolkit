import  argparse, sys

# -- Funtions that handle each subcommand --
def get_audit(args):
    '''it execute when the user tpes pytnon &&& audit'''
    print(f"[audit] Terget: {args.target}")

    if args.target == "local":
        print("Auditing the system")
        #TODO datos = run_audit()
        #print(datos)
        
    elif args.target == "api":
        if not args.url:
            print("Error: --url es requerido cuando target es 'api'")
            sys.exit(1)
        print(f"Auditing API: {args.url}")


def get_report(args):
    print(f"[report] Format: {args.format} Output: {args.output}")


def get_notify(args):
    print(f"[notify] Channel: {args.channel}")


# -- CLI defination -- 

def parser_build():
    parser = argparse.ArgumentParser(description="DevOps Automation Toolkit",
        epilog="Example: python main.py audit --target local")
    subparser = parser.add_subparsers(dest="command", metavar="COMmAND", required=True)

    audit = subparser.add_parser('audit', help="Audita el sistema local o una API")
    audit.add_argument('--target' ,choices=['local', 'api'], required=True)
    audit.add_argument('--url', help='Only for api audit')
    audit.set_defaults(func=get_audit)

    report = subparser.add_parser('report', help='generates a report in the format of your preference and where you want it')
    report.add_argument('--format',choices=['json', 'html', 'csv'], default='json', help='you can chosse between json html and csv format')
    report.add_argument('--output', default='./reports/', help='chosse where you want it')
    report.set_defaults(func=get_report)

    notify = subparser.add_parser('notify', help='it gives you a notification :)')
    notify.add_argument('--channel', choices=['slack', 'dicord'], required=True, help=('it notifies and you can chosse where you want it '))
    notify.set_defaults(func=get_notify)

    return parser


if __name__ == "__main__":
    parser = parser_build()
    args = parser.parse_args()
    args.func(args)
    


