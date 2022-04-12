import argparse
import traceback
import sys
import os
from cajdecrypt import decrypt_file
from cajparser import CAJParser, SupportException
from utils import add_outlines

class CustomException(Exception):
    pass

def main():
    parser = argparse.ArgumentParser(epilog="Following GNU General Public License v3.0. Source code can be found at: https://github.com/guest0417/CAJ_toolkit. NO ILLEGAL ACTIVITIES. Users may not use this programme to conduct or pursue any illegal activities, including but not limited to, distributing or viewing any illegal content, engaging in any activity in violation of OFAC regulations, and/or illegally downloading any copyrighted content, or any other activity that violates any intellectual property rights, and any such conduct using the program may result in immediate termination of the permission using this program.")
    subparsers = parser.add_subparsers(help="commands", dest="command")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt locked PDF to normal PDF.")
    decrypt_parser.add_argument("-i","--input", dest="src", help="Path to the PDF file.", required=True)
    decrypt_parser.add_argument("-o", "--output", dest="dst", help="Output path to the PDF file.", required=False)

    show_parser = subparsers.add_parser("show", help="Show the information of the CAJ file.")
    show_parser.add_argument("-i","--input", dest="src", help="Path to the CAJ file.", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert the CAJ file to PDF file.")
    convert_parser.add_argument("-i","--input", dest="src", help="Path to the CAJ file.", required=True)
    convert_parser.add_argument("-o", "--output", dest="dst", help="Output path to the PDF file.", required=False)

    outlines_parser = subparsers.add_parser("outlines", help="Extract outlines from the CAJ file and add it to PDF file.")
    outlines_parser.add_argument("-i","--input", dest="src", help="Path to the CAJ file.", required=True)
    outlines_parser.add_argument("-o", "--output", dest="dst", help="Path to the PDF file.", required=True)

    parse_parser = subparsers.add_parser("parse", help="Parse CAJ file for debugging/development")
    parse_parser.add_argument("-i","--input", dest="src", help="Path to the CAJ file.", required=True)

    text_extract_parser = subparsers.add_parser("text_extract", help="Parse CAJ file for debugging/development")
    text_extract_parser.add_argument("-i","--input", dest="src", help="Path to the CAJ file.", required=True)

    args = parser.parse_args()

    try:
        sys.argv[1]
    except IndexError:
        parser.print_help()

    if args.command == "decrypt":
        if args.dst is None:
            if args.src.endswith(".caj"):
                args.dst = args.src.replace(".caj", ".pdf")
            elif (len(args.src) > 4 and (args.src[-4] == '.' or args.src[-3] == '.') and not args.src.endswith(".pdf")):
                args.dst = os.path.splitext(args.src)[0] + ".pdf"
            else:
                args.dst = args.src + ".pdf"
        if not os.path.isfile(args.src):
            print("输入文件不存在")
            sys.exit(0)
        if os.path.isfile(args.dst):
            ans = input("文件 {} 已存在，继续运行将覆盖该文件，是否继续 [y/N]: ".format(args.dst))
            if ans.lower() not in ["y", "yes"]:
                sys.exit(0)
        decrypt_file(args.src, args.dst)

    if args.command == "show":
        if not os.path.isfile(args.src):
            print("输入文件不存在")
            sys.exit(0)
        caj = CAJParser(args.src)
        if caj.format == "PDF" or caj.format == "KDH":
            print("File: {0}\nType: {1}\n".format(args.src, caj.format))
        else:
            print("File: {0}\nType: {1}\nPage count: {2}\nOutlines count: {3}\n".format(
                args.src,
                caj.format,
                caj.page_num,
                caj.toc_num
            ))

    if args.command == "convert":
        if not os.path.isfile(args.src):
            print("输入文件不存在")
            sys.exit(0)
        if args.dst is None:
            if args.src.endswith(".caj"):
                args.dst = args.src.replace(".caj", ".pdf")
            elif (len(args.src) > 4 and (args.src[-4] == '.' or args.src[-3] == '.') and not args.src.endswith(".pdf")):
                args.dst = os.path.splitext(args.src)[0] + ".pdf"
            else:
                args.dst = args.src + ".pdf"
        if os.path.isfile(args.dst):
            ans = input("文件 {} 已存在，继续运行将覆盖该文件，是否继续 [y/N]: ".format(args.dst))
            if ans.lower() not in ["y", "yes"]:
                sys.exit(0)
        caj = CAJParser(args.src)
        caj.convert(args.dst)

    if args.command == "outlines":
        caj = CAJParser(args.src)
        if caj.format == "PDF" or caj.format == "KDH":
            raise SystemExit("Unsupported file type: {0}.".format(caj.format))
        toc = caj.get_toc()
        add_outlines(toc, args.dst, "tmp.pdf")
        os.replace("tmp.pdf", args.dst)

    if args.command == "text_extract":
        caj = CAJParser(args.src)
        caj.text_extract()

    if args.command == "parse":
        caj = CAJParser(args.src)
        caj.parse()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("User abort")
        sys.exit(0)
    except SupportException:
        print("[Error] Unsupported format")
        sys.exit(0)
    except (CustomException, Exception) as exc:
        if not isinstance(exc, CustomException):
            print("[Error] 未知错误: ", str(exc))
        else:
            print("[Error]", str(exc))
        print("-" * 64)
        traceback.print_exc()