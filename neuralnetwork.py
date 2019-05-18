import numpy as np
import scipy.special


class NeuralNetwork:
    def __init__(self, in_nodes, hidden_nodes, out_nodes, learning_grate, activation_function=scipy.special.expit):
        '''
        :param in_nodes: Количество входных вершин
        :param hidden_nodes: Количество скрытых вершин
        :param out_nodes: Количество выходных вершин
        :param learning_grate: Коэффициент обучения
        :param activation_function: Функция активации нейрона ( по умолчанию - сигмоида )
        '''
        self.inodes = in_nodes
        self.hnodes = hidden_nodes
        self.onodes = out_nodes
        self.lgrate = learning_grate
        self.wih = np.random.normal(0.0, pow(self.hnodes, -0.5), (self.hnodes, self.inodes))
        self.who = np.random.normal(0.0, pow(self.onodes, -0.5), (self.onodes, self.hnodes))
        self.af = activation_function

    def train(self, inputs_list, targets_list):
        # Прогоняем входные данные через сеть
        inputs = np.array(inputs_list, dtype=float, ndmin=2).T
        # Считаем вход для скрытого слоя
        hidden_inputs = np.dot(self.wih, inputs)
        # Применяем функцию активации
        hidden_outputs = self.af(hidden_inputs)
        # Аналогично для выходного слоя
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.af(final_inputs)

        # Транспонируем лист с ответами
        targets = np.array(targets_list, dtype=float, ndmin=2).T

        output_errors = targets - final_outputs
        hidden_errors = np.dot(self.who.T, output_errors)
        self.who += self.lgrate * np.dot(
            (output_errors * final_outputs * (1.0 - final_outputs)), np.transpose(hidden_outputs))
        self.wih += self.lgrate * np.dot(
            (hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), np.transpose(inputs))

    def query(self, inputs_list):
        # Транспонируем исходную матрицу
        inputs = np.array(inputs_list, dtype=float, ndmin=2).T
        # Считаем вход для скрытого слоя
        hidden_inputs = np.dot(self.wih, inputs)
        # Применяем функцию активации
        hidden_outputs = self.af(hidden_inputs)
        # Аналогично для выходного слоя
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.af(final_inputs)
        return final_outputs


if __name__ == '__main__':
    n = NeuralNetwork(3, 3, 1, learning_grate=1)
    Binary_inputs = np.array([[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]])
    OR_outputs = np.array([[0], [1], [1], [1]])
    AND_outputs = np.array([[0], [0], [0], [1]])
    XOR_outputs = np.array([[0], [1], [1], [0]])
    SELECTX1_outputs = np.array([[0], [0], [1], [1]])
    SELECTX2_outputs = np.array([[0], [1], [0], [1]])
    epochs = 1000
    for i in range(epochs):
        n.train(Binary_inputs, XOR_outputs)
    print(n.query(Binary_inputs))
    print()
    print(n.wih, n.who, sep='\n\n')
