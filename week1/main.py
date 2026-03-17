import csv
import math
import os
from collections import defaultdict

import matplotlib.pyplot as plt


BASE_DIR = r'./data'

TRAIN_FILE_NAME = 'train.csv'
TEST_FILE_NAME = 'test.csv'

AGE_GROUP_LABELS = [
    '10s',
    '20s',
    '30s',
    '40s',
    '50s',
    '60s',
    '70s+',
]

NUMERIC_COLUMNS = [
    'Age',
    'RoomService',
    'FoodCourt',
    'ShoppingMall',
    'Spa',
    'VRDeck',
]

CATEGORICAL_COLUMNS = [
    'HomePlanet',
    'CryoSleep',
    'Cabin',
    'Destination',
    'VIP',
]


def build_file_path(file_name):
    return os.path.join(BASE_DIR, file_name)


def read_csv_file(file_path):
    with open(file_path, 'r', encoding='utf-8', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]


def merge_rows(train_rows, test_rows):
    return train_rows + test_rows


def parse_bool(value):
    if value is None:
        return None

    text = value.strip()

    if text == 'True':
        return 1

    if text == 'False':
        return 0

    return None


def parse_float(value):
    if value is None:
        return None

    text = value.strip()

    if text == '':
        return None

    try:
        return float(text)
    except ValueError:
        return None


def get_age_group(age_value):
    age = parse_float(age_value)

    if age is None:
        return None

    if 10 <= age < 20:
        return '10s'

    if 20 <= age < 30:
        return '20s'

    if 30 <= age < 40:
        return '30s'

    if 40 <= age < 50:
        return '40s'

    if 50 <= age < 60:
        return '50s'

    if 60 <= age < 70:
        return '60s'

    if age >= 70:
        return '70s+'

    return None


def get_rows_with_transported(rows):
    filtered_rows = []

    for row in rows:
        transported = parse_bool(row.get('Transported'))

        if transported is not None:
            filtered_rows.append(row)

    return filtered_rows


def calculate_numeric_correlation(rows, column_name):
    x_values = []
    y_values = []

    for row in rows:
        x_value = parse_float(row.get(column_name))
        y_value = parse_bool(row.get('Transported'))

        if x_value is None or y_value is None:
            continue

        x_values.append(x_value)
        y_values.append(y_value)

    count = len(x_values)

    if count < 2:
        return None

    mean_x = sum(x_values) / count
    mean_y = sum(y_values) / count

    numerator = 0.0
    sum_square_x = 0.0
    sum_square_y = 0.0

    for index in range(count):
        diff_x = x_values[index] - mean_x
        diff_y = y_values[index] - mean_y

        numerator += diff_x * diff_y
        sum_square_x += diff_x * diff_x
        sum_square_y += diff_y * diff_y

    denominator = math.sqrt(sum_square_x * sum_square_y)

    if denominator == 0:
        return None

    return numerator / denominator


def calculate_categorical_strength(rows, column_name):
    grouped = defaultdict(lambda: {'total': 0, 'transported': 0})

    for row in rows:
        value = row.get(column_name)
        transported = parse_bool(row.get('Transported'))

        if value is None or transported is None:
            continue

        text = value.strip()

        if text == '':
            continue

        grouped[text]['total'] += 1
        grouped[text]['transported'] += transported

    total_count = 0
    total_transported = 0

    for stats in grouped.values():
        total_count += stats['total']
        total_transported += stats['transported']

    if total_count == 0:
        return None

    overall_rate = total_transported / total_count
    weighted_gap = 0.0

    for stats in grouped.values():
        group_rate = stats['transported'] / stats['total']
        weight = stats['total'] / total_count
        weighted_gap += weight * abs(group_rate - overall_rate)

    return weighted_gap


def find_most_related_feature(train_rows):
    scores = []

    for column_name in NUMERIC_COLUMNS:
        correlation = calculate_numeric_correlation(train_rows, column_name)

        if correlation is None:
            continue

        scores.append(
            {
                'column': column_name,
                'score': abs(correlation),
                'raw_score': correlation,
                'method': 'numeric_correlation',
            }
        )

    for column_name in CATEGORICAL_COLUMNS:
        strength = calculate_categorical_strength(train_rows, column_name)

        if strength is None:
            continue

        scores.append(
            {
                'column': column_name,
                'score': strength,
                'raw_score': strength,
                'method': 'categorical_gap',
            }
        )

    if not scores:
        return None, []

    scores.sort(key=lambda item: item['score'], reverse=True)

    return scores[0], scores


def build_age_transport_summary(train_rows):
    summary = {
        label: {'transported': 0, 'not_transported': 0}
        for label in AGE_GROUP_LABELS
    }

    for row in train_rows:
        age_group = get_age_group(row.get('Age'))
        transported = parse_bool(row.get('Transported'))

        if age_group is None or transported is None:
            continue

        if transported == 1:
            summary[age_group]['transported'] += 1
        else:
            summary[age_group]['not_transported'] += 1

    return summary


def plot_age_transport_summary(summary):
    transported_counts = []
    not_transported_counts = []

    for label in AGE_GROUP_LABELS:
        transported_counts.append(summary[label]['transported'])
        not_transported_counts.append(summary[label]['not_transported'])

    x_positions = list(range(len(AGE_GROUP_LABELS)))

    plt.figure(figsize=(10, 6))
    plt.plot(
        x_positions,
        transported_counts,
        marker='o',
        label='Transported',
    )
    plt.plot(
        x_positions,
        not_transported_counts,
        marker='o',
        label='Not Transported',
    )
    plt.xticks(x_positions, AGE_GROUP_LABELS)
    plt.title('Transported Status by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Passenger Count')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def build_destination_age_summary(all_rows):
    summary = defaultdict(lambda: {label: 0 for label in AGE_GROUP_LABELS})

    for row in all_rows:
        destination = row.get('Destination')
        age_group = get_age_group(row.get('Age'))

        if destination is None or age_group is None:
            continue

        destination_text = destination.strip()

        if destination_text == '':
            continue

        summary[destination_text][age_group] += 1

    return summary


def plot_destination_age_summary(summary):
    destinations = sorted(summary.keys())

    if not destinations:
        return

    x_positions = list(range(len(destinations)))
    bottom_values = [0] * len(destinations)

    plt.figure(figsize=(12, 7))

    for label in AGE_GROUP_LABELS:
        values = []

        for destination in destinations:
            values.append(summary[destination][label])

        plt.bar(
            x_positions,
            values,
            bottom=bottom_values,
            label=label,
        )

        for index, value in enumerate(values):
            bottom_values[index] += value

    plt.xticks(x_positions, destinations, rotation=15)
    plt.title('Age Group Distribution by Destination')
    plt.xlabel('Destination')
    plt.ylabel('Passenger Count')
    plt.legend(title='Age Group')
    plt.tight_layout()
    plt.show()


def print_row_counts(train_rows, test_rows, merged_rows):
    print('train.csv row count :', len(train_rows))
    print('test.csv row count  :', len(test_rows))
    print('merged row count    :', len(merged_rows))


def print_related_feature_result(best_feature, scores):
    print()
    print('[Most related feature to Transported]')

    if best_feature is None:
        print('No feature could be calculated.')
        return

    print('Feature :', best_feature['column'])
    print('Method  :', best_feature['method'])
    print('Score   :', round(best_feature['raw_score'], 6))

    print()
    print('[Top feature scores]')

    for item in scores:
        print(
            '-',
            item['column'],
            '| method =',
            item['method'],
            '| score =',
            round(item['raw_score'], 6),
        )


def main():
    train_file_path = build_file_path(TRAIN_FILE_NAME)
    test_file_path = build_file_path(TEST_FILE_NAME)

    train_rows = read_csv_file(train_file_path)
    test_rows = read_csv_file(test_file_path)
    merged_rows = merge_rows(train_rows, test_rows)

    print_row_counts(train_rows, test_rows, merged_rows)

    train_rows_for_analysis = get_rows_with_transported(train_rows)

    best_feature, scores = find_most_related_feature(
        train_rows_for_analysis
    )
    print_related_feature_result(best_feature, scores)

    age_transport_summary = build_age_transport_summary(
        train_rows_for_analysis
    )
    plot_age_transport_summary(age_transport_summary)

    destination_age_summary = build_destination_age_summary(merged_rows)
    plot_destination_age_summary(destination_age_summary)


if __name__ == '__main__':
    main()