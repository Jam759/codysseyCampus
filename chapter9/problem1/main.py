from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt


def print_data_info(name, values):
    print(f'[{name}]')
    print(f'shape: {values.shape}')
    print(f'ndim: {values.ndim}')
    print(f'dtype: {values.dtype}')
    print(f'first 5 data:\n{values[:5]}')
    print()


def print_split_info(name, values):
    print(f'{name} shape: {values.shape}')


def draw_iris_graph(data, target, target_names, feature_names):
    x_index = 0
    y_index = 1

    plt.figure(figsize=(8, 6))

    for target_value, target_name in enumerate(target_names):
        x_values = data[target == target_value, x_index]
        y_values = data[target == target_value, y_index]

        plt.scatter(
            x_values,
            y_values,
            label=target_name
        )

    plt.xlabel(feature_names[x_index])
    plt.ylabel(feature_names[y_index])
    plt.title('Iris Data Distribution')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    iris_dataset = load_iris()

    print('[DESCR]')
    print(iris_dataset['DESCR'])
    print()

    print('[target_names]')
    print(iris_dataset['target_names'])
    print()

    print('[feature_names]')
    print(iris_dataset['feature_names'])
    print()

    data = iris_dataset['data']
    target = iris_dataset['target']
    target_names = iris_dataset['target_names']
    feature_names = iris_dataset['feature_names']

    print_data_info('data', data)
    print_data_info('target', target)

    X_train, X_test, y_train, y_test = train_test_split(
        data,
        target,
        test_size=0.25,
        random_state=0,
        stratify=target
    )

    print('[train_test_split result]')
    print_split_info('X_train', X_train)
    print_split_info('X_test', X_test)
    print_split_info('y_train', y_train)
    print_split_info('y_test', y_test)
    print()

    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(X_train, y_train)

    sample_data = [[5, 2.9, 1, 0.2]]
    prediction = model.predict(sample_data)
    predicted_name = target_names[prediction[0]]

    print('[prediction]')
    print(f'input data: {sample_data}')
    print(f'predicted target: {prediction[0]}')
    print(f'predicted target name: {predicted_name}')
    print()

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    print('[model score]')
    print(f'train score: {train_score:.4f}')
    print(f'test score: {test_score:.4f}')
    print()

    draw_iris_graph(data, target, target_names, feature_names)


if __name__ == '__main__':
    main()