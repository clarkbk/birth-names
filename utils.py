import re


class Utils(object):
    class US(object):
        @staticmethod
        def is_valid_file(file):
            return file.endswith('.txt')

    class UK(object):
        @staticmethod
        def is_valid_file(file):
            return (
                file.endswith('.xls') and
                not file.startswith('historicname')
            )

        @staticmethod
        def extract_data_from_filename(file):
            file = file.replace('.xls', '')
            return file.split('_')

        @staticmethod
        def find_correct_worksheet(book):
            if book.nsheets >= 6:
                pttrn = re.compile('table 6', re.IGNORECASE)
            else:
                pttrn = re.compile('table 3', re.IGNORECASE)
            return [i for i, sht in enumerate(book.sheet_names()) if pttrn.search(sht)][0]

        @staticmethod
        def find_start_row(sheet):
            for i in range(10):
                if all(x in sheet.row_values(i) for x in ['Rank', 'Name']):
                    return i

        @staticmethod
        def is_valid_row(row):
            return (
                len(row) == 3 and
                row[0].ctype == 2 and
                row[1].ctype == 1 and
                row[2].ctype == 2
            )

        @staticmethod
        def cell_is_empty(cell):
            return cell.ctype == 0
