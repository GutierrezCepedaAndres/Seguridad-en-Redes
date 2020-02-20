
import argparse


def main():
    parser = argparse.ArgumentParser(description='gpg-cracker')
    parser.add_argument('--len', type=int, help='Maximum length of the symmetric key', required=True)
    parser.add_argument('--charset', type=str, help='Key character set', required=True)
    parser.add_argument('--threads', type=int, help='Number of threads. Default 1', default=1)

if __name__ == "__main__":
    main()