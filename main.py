# main.py
import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from ui.MainWindow import MainWindow

def main():
	app = QApplication(sys.argv)
	main_window = MainWindow()

	cursor_pos = QDesktopWidget().cursor().pos()
	screen_number = QDesktopWidget().screenNumber(cursor_pos)
	screen = QDesktopWidget().screenGeometry(screen_number)
	center_x = screen.left() + (screen.width() - main_window.width()) // 2
	center_y = screen.top() + (screen.height() - main_window.height()) // 2
	main_window.move(center_x, center_y)

	main_window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()