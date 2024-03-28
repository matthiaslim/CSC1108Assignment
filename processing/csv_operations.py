import csv


def read_csv(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        for row in csv.DictReader(csvfile):
            data.append(row)
    return data


def write_to_csv(data, file_path, columns):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        if columns:
            fieldnames = columns  # Assuming all dictionaries have the same keys
        else:
            fieldnames = data[0].keys()

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
