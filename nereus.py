from argparse import ArgumentParser
from src.biomark import retrieveData
from src.postgres import database


def main():
    # Main arguments included in command line execution of program,
    # useful for running program from a systemd service file.
    parser = ArgumentParser(description='Program to retrieve PIT data from IS1001s')
    parser.add_argument('client_file', type=str, help='/path/to/client/file.txt')
    args = parser.parse_args()

    retrieve = retrieveData(args.client_file)
    db = database()

    raw_data = retrieve.pitTags()
    formatted = retrieve.formatTagData(raw_data)
    db.append(formatted)

if __name__ == '__main__':
    main()

