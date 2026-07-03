
# main.py
import argparse
import sys
from src.auditor import run_formated_audit, run_raw_audit

from src.reporters import generate_report
# from src.notifier import send_notification




def cmd_audit(args):
    """Se ejecuta cuando el usuario escribe: python main.py audit ..."""
    print(f"\n[audit] Target: {args.target}")
    
    if args.target == "local":
        print("\nAuditando sistema local...\n")
        
        datos = run_formated_audit()
        print(datos)
        
    elif args.target == "api":
        if not args.url:
            print("Error: --url es requerido cuando target es 'api'")
            sys.exit(1)
        print(f"Auditando API: {args.url}")


def cmd_report(args):
    """Se ejecuta cuando el usuario escribe: python main.py report ..."""
    print(f"[report] Formato: {args.format} | Destino: {args.output}")
    # Cuando tengas reporters.py listo:
    
    generate_report(format=args.format, output=args.output)


def cmd_notify(args):
    """Se ejecuta cuando el usuario escribe: python main.py notify ..."""
    print(f"[notify] Canal: {args.channel}")
    # Cuando tengas notifier.py listo:
    # send_notification(channel=args.channel)


# --- Definición del CLI ---

def build_parser():
    parser = argparse.ArgumentParser(
        description="DevOps Automation Toolkit",
        epilog="Ejemplo: python main.py audit --target local"
    )
    
    subparsers = parser.add_subparsers(dest="command", metavar="COMANDO")
    subparsers.required = True  # Error si no se escribe ningún subcomando

    # Subcomando: audit
    audit = subparsers.add_parser("audit", help="Audita el sistema local o una API")
    audit.add_argument(
        "--target",
        choices=["local", "api"],
        required=True,
        help="Qué auditar: 'local' para el sistema, 'api' para una URL"
    )
    audit.add_argument(
        "--url",
        help="URL a auditar (solo necesario con --target api)"
    )
    audit.set_defaults(func=cmd_audit)  # Conecta este subcomando con su función

    # Subcomando: report
    report = subparsers.add_parser("report", help="Genera un reporte")
    report.add_argument(
        "--format",
        choices=["json", "csv", "html"],
        default="json",
        help="Formato del reporte (default: json)"
    )
    report.add_argument(
        "--output",
        default="./reports/",
        help="Carpeta donde guardar el reporte (default: ./reports/)"
    )
    report.set_defaults(func=cmd_report)

    # Subcomando: notify
    notify = subparsers.add_parser("notify", help="Envía una notificación")
    notify.add_argument(
        "--channel",
        choices=["slack", "discord"],
        required=True,
        help="Canal de notificación"
    )
    notify.set_defaults(func=cmd_notify)

    return parser




if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)  # Llama a cmd_audit, cmd_report o cmd_notify según el comando
