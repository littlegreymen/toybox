import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QTextEdit, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from sympy import sympify, latex
from shapesimilarity import shape_similarity


def blend_colors(color1, color2, alpha=0.5):
    # Blend two RGB tuples (each 0-1 floats)
    return tuple(alpha * c1 + (1 - alpha) * c2 for c1, c2 in zip(color1, color2))


class FunctionInput(QWidget):
    def __init__(self, label):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(f"<b>{label}</b>")
        self.textbox = QTextEdit()
        self.math_display = QLabel()
        self.status_label = QLabel("Status: Not checked")
        self.math_display.setWordWrap(True)
        self.math_display.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.math_display)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def get_function_text(self):
        return self.textbox.toPlainText()

    def update_display(self, func_expr):
        try:
            expr_for_parse = func_expr.replace("np.", "")
            sym_expr = sympify(expr_for_parse)
            latex_str = latex(sym_expr)
            self.math_display.setText(f"\\[ {latex_str} \\]")
            self.status_label.setText("✅ Parsed successfully")
            self.status_label.setStyleSheet("color: green;")
            return True
        except Exception:
            self.math_display.setText("Invalid expression")
            self.status_label.setText("❌ Parse error")
            self.status_label.setStyleSheet("color: red;")
            return False


class PlotCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def plot_functions(self, x, y1, y2, similarity):
        self.ax.clear()
        blue = (0, 0, 1)
        red = (1, 0, 0)
        if similarity >= 0.9999:
            purple = blend_colors(blue, red, 0.5)
            self.ax.plot(x, y1, label='f1(x) & f2(x)', color=purple)
        else:
            self.ax.plot(x, y1, label='f1(x)', color='blue')
            self.ax.plot(x, y2, label='f2(x)', color='red')
        self.ax.legend()
        self.ax.set_title("Function Plots")
        self.draw()


class SimilarityApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Function Shape Similarity")

        layout = QHBoxLayout()

        # Left Pane
        self.func1_input = FunctionInput("Function 1: f(x)")
        self.func2_input = FunctionInput("Function 2: f(x)")
        self.compare_button = QPushButton("Compare")
        self.compare_button.clicked.connect(self.update)

        left_pane = QVBoxLayout()
        left_pane.addWidget(self.func1_input)
        left_pane.addWidget(self.func2_input)
        left_pane.addWidget(self.compare_button)

        # Right Pane
        self.plot = PlotCanvas()
        self.similarity_display = QLabel("Similarity: ?")
        self.similarity_display.setAlignment(Qt.AlignCenter)
        self.similarity_display.setStyleSheet(
            "font-size: 24px; color: green; font-weight: bold;"
        )

        right_pane = QVBoxLayout()
        right_pane.addWidget(self.plot)
        right_pane.addWidget(self.similarity_display)

        layout.addLayout(left_pane, 1)
        layout.addLayout(right_pane, 2)
        self.setLayout(layout)

    def evaluate_function(self, expr, x_vals):
        try:
            code = compile(expr, "<string>", "eval")
            y_vals = np.array([
                eval(code, {"x": val, "np": np, "__builtins__": {}})
                for val in x_vals
            ], dtype=float)
            return y_vals
        except Exception as e:
            print(f"Evaluation error: {e}")
            return None

    def update(self):
        f1_text = self.func1_input.get_function_text().strip()
        f2_text = self.func2_input.get_function_text().strip()

        f1_ok = self.func1_input.update_display(f1_text)
        f2_ok = self.func2_input.update_display(f2_text)

        if not f1_ok or not f2_ok:
            self.similarity_display.setText("Please fix parse errors above")
            return

        x_vals = np.linspace(-10, 10, 400)
        y1 = self.evaluate_function(f1_text, x_vals)
        y2 = self.evaluate_function(f2_text, x_vals)

        if y1 is None or y2 is None:
            self.similarity_display.setText("Evaluation error: check expressions")
            return

        if y1.shape != y2.shape or not np.all(np.isfinite(y1)) or not np.all(np.isfinite(y2)):
            self.similarity_display.setText("Invalid values: NaN, Inf, or shape mismatch")
            return

        # Compute 2D shape similarity
        try:
            shape1 = np.column_stack((x_vals, y1))
            shape2 = np.column_stack((x_vals, y2))
            similarity = shape_similarity(shape1, shape2)
            self.similarity_display.setText(f"Similarity: {similarity:.4f}")
        except Exception as e:
            self.similarity_display.setText(f"Similarity error: {str(e)}")
            similarity = 0.0  # fallback so plotting doesn't fail

        # Plot the curves with color blending if similarity ~ 1
        self.plot.plot_functions(x_vals, y1, y2, similarity)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SimilarityApp()
    win.resize(1000, 600)
    win.show()
    sys.exit(app.exec())
