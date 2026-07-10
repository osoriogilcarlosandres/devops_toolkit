#imports
import argparse, sys, logging
from src.auditor import  audit_api, local_audit
from src.reports import generate_report
from src.notifer import send_notification


from src.config_parser import get_config

config = get_config()

logger = logging.getLogger(__name__)


def cmd_audit(args):
    
    logger.info(f"[audit] Target: {args.target}")
    
    if args.target.lower() == "local":
        logger.info("Auditing local system...")
        
        local_audit()

        
    elif args.target.lower() == "api":
        if not args.url:
            logger.error("Error: --url It is required when target is 'api'.")
            sys.exit(1)
        audit_api(args.url)


def cmd_report(args):
    logger.info(f"[report] Formato: {args.format} | Destino: {args.output}")
    generate_report(format=args.format.lower(), output=args.output)


def cmd_notify(args):
    logger.info(f"[notify] Canal: {args.channel}")
    send_notification(channel=args.channel)

def build_parser():
    parser = argparse.ArgumentParser(
        description="DevOps Automation Toolkit",
        epilog="Example: python main.py audit --target local"
    )
    
    subparsers = parser.add_subparsers(dest="command", metavar="COMANDO")
    subparsers.required = True  # Error si no se escribe ningún subcomando

    # Subcomando: audit
    audit = subparsers.add_parser("audit", help="Audits the local system or an API.")
    audit.add_argument(
        "--target",
        choices=["local", "api"],
        required=True,
        help="What to audit: 'local' for the system, 'api' for a URL."
    )
    audit.add_argument(
        "--url",
        help="URL to audit (only required with --target api)"
    )
    audit.set_defaults(func=cmd_audit)  # Conecta este subcomando con su función

    # Subcomando: report
    report = subparsers.add_parser("report", help="Genera un reporte")
    report.add_argument(
        "--format",
        choices=["json", "csv", "html"],
        default=config["default_format"],
        help=f"Report format (default: {config["default_format"]})"
    )
    report.add_argument(
        "--output",
        default=config["default_output"],
        help=f"directory where the report will be saved (default: {config["default_output"]})"
    )
    report.set_defaults(func=cmd_report)

    # Subcomando: notify
    notify = subparsers.add_parser("notify", help="Send a notification")
    notify.add_argument(
        "--channel",
        choices=["slack", "discord"],
        
        required=True,
        help="Notification channel"
    )
    notify.set_defaults(func=cmd_notify)

    return parser




if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)  # Llama a cmd_audit, cmd_report o cmd_notify según el comando

