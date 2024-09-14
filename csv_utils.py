import csv

def read_first_column(file_path):
    first_column_data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader, None)
        for row in reader:
            if row:
                first_column_data.append(row[0])
    return first_column_data

def write_lists_to_csv(file_path, *lists):
    num_rows = len(lists[0])
    if not all(len(lst) == num_rows for lst in lists):
        raise ValueError("所有列表的长度必须相同")
    with open(file_path, mode='w', newline='', encoding='gbk') as file:
        writer = csv.writer(file)
        for rows in zip(*lists):
            writer.writerow(rows)