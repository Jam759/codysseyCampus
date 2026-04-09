import pandas as pd
import matplotlib.pyplot as plt


FILE_PATH = (
    r'../../data/cap4_p2/data.csv'
)

BASE_COLUMNS = ['행정구역별(시군구)', '성별', '연령별']
DETAILED_AGE_ORDER = [
    '15세미만',
    '15~19세',
    '20~24세',
    '25~29세',
    '30~34세',
    '35~39세',
    '40~44세',
    '45~49세',
    '50~54세',
    '55~59세',
    '60~64세',
    '65~69세',
    '70~74세',
    '75~79세',
    '80~84세',
    '85세이상',
]
AGE_LABEL_MAP = {
    '15세미만': 'Under 15',
    '15~19세': '15-19',
    '20~24세': '20-24',
    '25~29세': '25-29',
    '30~34세': '30-34',
    '35~39세': '35-39',
    '40~44세': '40-44',
    '45~49세': '45-49',
    '50~54세': '50-54',
    '55~59세': '55-59',
    '60~64세': '60-64',
    '65~69세': '65-69',
    '70~74세': '70-74',
    '75~79세': '75-79',
    '80~84세': '80-84',
    '85세이상': '85+',
}


def read_csv_file(file_path):
    encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']

    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError('CSV 파일의 인코딩을 확인할 수 없습니다.')


def find_general_household_columns(raw_df):
    info_row = raw_df.iloc[0]
    year_columns = []

    for column_name in raw_df.columns:
        if column_name in BASE_COLUMNS:
            continue

        if str(info_row[column_name]).strip() == '일반가구원':
            year_columns.append(column_name)

    if not year_columns:
        raise ValueError('일반가구원에 해당하는 연도 컬럼을 찾지 못했습니다.')

    return year_columns


def prepare_population_data(raw_df, year_columns):
    data_df = raw_df.iloc[1:].copy()

    if '전국' in data_df['행정구역별(시군구)'].values:
        data_df = data_df[data_df['행정구역별(시군구)'] == '전국'].copy()

    for column_name in year_columns:
        data_df[column_name] = pd.to_numeric(
            data_df[column_name].astype(str).str.replace(',', '', regex=False),
            errors='coerce',
        )

    return data_df


def create_yearly_gender_table(data_df, year_columns):
    yearly_gender_df = data_df[
        (data_df['연령별'] == '합계') & (data_df['성별'].isin(['남자', '여자']))
    ][['성별'] + year_columns].copy()

    yearly_gender_df = yearly_gender_df.set_index('성별').T
    yearly_gender_df.index.name = '연도'
    yearly_gender_df['합계'] = yearly_gender_df.sum(axis=1)

    return yearly_gender_df


def create_age_table(data_df, year_columns):
    age_df = data_df[
        (data_df['성별'] == '계') & (data_df['연령별'].isin(DETAILED_AGE_ORDER))
    ][['연령별'] + year_columns].copy()

    age_df = age_df.set_index('연령별').reindex(DETAILED_AGE_ORDER)

    return age_df


def create_gender_age_table(data_df, year_columns, gender):
    gender_age_df = data_df[
        (data_df['성별'] == gender) & (data_df['연령별'].isin(DETAILED_AGE_ORDER))
    ][['연령별'] + year_columns].copy()

    gender_age_df = gender_age_df.set_index('연령별').reindex(DETAILED_AGE_ORDER)

    return gender_age_df


def draw_single_gender_graph(gender_age_df, year_columns, gender_name, file_name):
    year_values = [int(year) for year in year_columns]

    plt.figure(figsize=(15, 8))

    for age_group in gender_age_df.index:
        plt.plot(
            year_values,
            gender_age_df.loc[age_group].values,
            marker='o',
            label=AGE_LABEL_MAP[age_group],
        )

    plt.title(f'{gender_name} General Household Population by Age Group')
    plt.xlabel('Year')
    plt.ylabel('Population')
    plt.xticks(year_values)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.02, 1.0), loc='upper left')
    plt.tight_layout()
    plt.show()


def draw_gender_age_graph(male_age_df, female_age_df, year_columns):
    draw_single_gender_graph(
        male_age_df,
        year_columns,
        'Male',
        'male_age_population_trend.png',
    )
    draw_single_gender_graph(
        female_age_df,
        year_columns,
        'Female',
        'female_age_population_trend.png',
    )


def create_bonus_report(age_df, male_age_df, female_age_df, year_columns):
    start_year = year_columns[0]
    end_year = year_columns[-1]

    total_change = age_df[end_year] - age_df[start_year]
    total_change_rate = ((age_df[end_year] / age_df[start_year]) - 1) * 100

    elderly_groups = ['65~69세', '70~74세', '75~79세', '80~84세', '85세이상']
    youth_groups = ['15세미만', '15~19세', '20~24세', '25~29세', '30~34세']

    elderly_start = age_df.loc[elderly_groups, start_year].sum()
    elderly_end = age_df.loc[elderly_groups, end_year].sum()

    youth_start = age_df.loc[youth_groups, start_year].sum()
    youth_end = age_df.loc[youth_groups, end_year].sum()

    max_increase_group = total_change.idxmax()
    max_decrease_group = total_change.idxmin()
    max_increase_value = int(total_change[max_increase_group])
    max_decrease_value = abs(int(total_change[max_decrease_group]))

    max_rate_increase_group = total_change_rate.idxmax()
    max_rate_decrease_group = total_change_rate.idxmin()

    male_85_change = int(
        male_age_df.loc['85세이상', end_year] - male_age_df.loc['85세이상', start_year]
    )
    female_85_change = int(
        female_age_df.loc['85세이상', end_year] - female_age_df.loc['85세이상', start_year]
    )

    report_lines = [
        '보너스 과제 리포트',
        f'- 분석 기간: {start_year}년 ~ {end_year}년',
        (
            f'- 가장 크게 증가한 연령대는 {max_increase_group}이며, '
            f'{max_increase_value:,}명 증가했습니다.'
        ),
        (
            f'- 가장 크게 감소한 연령대는 {max_decrease_group}이며, '
            f'{max_decrease_value:,}명 감소했습니다.'
        ),
        (
            f'- 증가율이 가장 높은 연령대는 {max_rate_increase_group}이며, '
            f'{total_change_rate[max_rate_increase_group]:.2f}% 증가했습니다.'
        ),
        (
            f'- 감소율이 가장 큰 연령대는 {max_rate_decrease_group}이며, '
            f'{abs(total_change_rate[max_rate_decrease_group]):.2f}% 감소했습니다.'
        ),
        (
            f'- 고령층(65세 이상 세부 연령대 합계)은 '
            f'{elderly_start:,}명에서 {elderly_end:,}명으로 증가했습니다.'
        ),
        (
            f'- 저연령층(15세미만~30~34세 합계)은 '
            f'{youth_start:,}명에서 {youth_end:,}명으로 감소했습니다.'
        ),
        (
            f'- 85세 이상은 남자 {male_85_change:,}명, '
            f'여자 {female_85_change:,}명 증가하여 여자 증가 폭이 더 컸습니다.'
        ),
        '- 전체적으로 저연령층은 감소하고, 60대 이후 고령층은 빠르게 증가하는 고령화 추세가 확인됩니다.',
        '- 특히 60~64세와 65~69세의 증가 폭이 매우 크며, 80세 이상 초고령층도 뚜렷하게 늘어났습니다.',
        '- 반면 15세미만, 15~19세, 20~24세는 지속적으로 감소하여 젊은 인구층 축소 흐름이 나타납니다.',
    ]

    report_text = '\n'.join(report_lines)

    return report_text


def main():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    raw_df = read_csv_file(FILE_PATH)
    year_columns = find_general_household_columns(raw_df)
    data_df = prepare_population_data(raw_df, year_columns)

    yearly_gender_df = create_yearly_gender_table(data_df, year_columns)
    age_df = create_age_table(data_df, year_columns)
    male_age_df = create_gender_age_table(data_df, year_columns, '남자')
    female_age_df = create_gender_age_table(data_df, year_columns, '여자')
    report_text = create_bonus_report(age_df, male_age_df, female_age_df, year_columns)

    print(f'분석 대상 기간: {year_columns[0]}년 ~ {year_columns[-1]}년')
    print()
    print('1. 남자 및 여자의 연도별 일반가구원 데이터 통계')
    print(yearly_gender_df.to_string())
    print()
    print('2. 연령별 일반가구원 데이터 통계')
    print(age_df.to_string())
    print()
    print('3. 보너스 과제 리포트')
    print(report_text)

    draw_gender_age_graph(male_age_df, female_age_df, year_columns)


if __name__ == '__main__':
    main()