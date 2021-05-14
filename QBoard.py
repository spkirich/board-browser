from PyQt5.QtCore import QIODevice, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort

class QBoard(QSerialPort):
    """Класс для взаимодействия с платами.

    Методы:
        open: Устанавливает соединение с платой.
    
    Сигналы:
        receivedMessage: Получено текстовое сообщение.
        receivedValue: Получено числовое значение.
    """

    receivedMessage = pyqtSignal(str)
    receivedValue = pyqtSignal(float)

    def __init__(self, portInfoOrName, parent=None):
        """Инициализирует объект идентификатором порта."""

        super(QBoard, self).__init__(portInfoOrName, parent)

        self.readyRead.connect(self.receive)

    def open(self):
        """Устанавливает соединение с платой."""

        return super(QBoard, self).open(QIODevice.ReadWrite)

    def receive(self):
        """Обрабатывает поступающие данные. Не использовать непосредственно!"""

        while self.canReadLine():
            try:
                line = self.readLine().data().decode()
            except UnicodeDecodeError:
                continue

            line = line.replace('\r', '').replace('\n', '')

            try:
                value = float(line)
            except ValueError:
                self.receivedMessage.emit(line)
                continue

            self.receivedValue.emit(value)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QInputDialog, QTextEdit
    from PyQt5.QtSerialPort import QSerialPortInfo

    import sys

    app = QApplication(sys.argv)

    portNames = map(lambda portInfo: portInfo.portName(),
        QSerialPortInfo.availablePorts())

    portName, ok = QInputDialog.getItem(None,
        'Serial port',
        'Select the serial port',
        portNames,
        editable=False)

    if not ok:
        sys.exit(1)

    board = QBoard(portName)
    board.open()

    textEdit = QTextEdit()

    appendMessage = lambda message: textEdit.append(
        '<i>{}</i>'.format(message))

    appendValue = lambda value: textEdit.append(
        '<b>{}</b>'.format(value))

    board.receivedMessage.connect(appendMessage)
    board.receivedValue.connect(appendValue)

    textEdit.show()

    sys.exit(app.exec_())
