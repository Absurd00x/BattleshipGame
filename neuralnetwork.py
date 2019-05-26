import numpy as np
import scipy.special


class NeuralNetwork:
    def __init__(self, in_nodes, hidden_nodes, out_nodes, learning_grate):
        '''
        :param in_nodes: Количество входных вершин
        :param hidden_nodes: Количество скрытых вершин
        :param out_nodes: Количество выходных вершин
        :param learning_grate: Коэффициент обучения
        '''
        self.inodes = in_nodes
        self.hnodes = hidden_nodes
        self.onodes = out_nodes
        self.lrate = learning_grate
        self.wih = np.random.normal(0.0, pow(self.hnodes, -0.5), (self.hnodes, self.inodes))
        self.who = np.random.normal(0.0, pow(self.onodes, -0.5), (self.onodes, self.hnodes))
        self.af = scipy.special.expit
        self.af_inv = scipy.special.logit

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
        self.who += self.lrate * np.dot(
            output_errors * final_outputs * (1 - final_outputs), np.transpose(hidden_outputs))
        self.wih += self.lrate * np.dot(
            hidden_errors * hidden_outputs * (1 - hidden_outputs), np.transpose(inputs))

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

    def backward_query(self, output_list):
        final_outputs = np.array(output_list, dtype=float, ndmin=2)
        final_inputs = self.af_inv(final_outputs)
        hidden_outputs = final_inputs.dot(self.who)

        # Приводим значения к области значений сигмоиды
        hidden_outputs -= np.min(hidden_outputs)
        hidden_outputs /= np.max(hidden_outputs)
        hidden_outputs *= 0.98
        hidden_outputs += 0.01

        hidden_inputs = self.af_inv(hidden_outputs)
        inputs = hidden_inputs.dot(self.wih)

        # Снова приводим
        inputs -= np.min(inputs)
        inputs /= np.max(inputs)
        inputs *= 0.98
        inputs += 0.01

        return inputs


if __name__ == '__main__':
    n = NeuralNetwork(3, 10, 1, learning_grate=1)
    Binary_inputs = np.array([[0.99, 0.01, 0.01], [0.99, 0.01, 0.99],
                              [0.99, 0.99, 0.01], [0.99, 0.99, 0.99]])
    OR_outputs = np.array([[0.01], [0.99], [0.99], [0.99]])
    AND_outputs = np.array([[0.01], [0.01], [0.01], [0.99]])
    XOR_outputs = np.array([[0.01], [0.99], [0.99], [0.01]])
    SELECTX1_outputs = np.array([[0.01], [0.01], [0.99], [0.99]])
    SELECTX2_outputs = np.array([[0.01], [0.99], [0.01], [0.99]])
    epochs = 10000
    for i in range(epochs):
        n.train(Binary_inputs, XOR_outputs)

    print(n.query(Binary_inputs))

    print(n.backward_query([0.99]))
