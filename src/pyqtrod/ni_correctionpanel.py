from PyQt6 import QtWidgets
from functools import partial


class CorrectionPanel(QtWidgets.QWidget):
    def __init__(self, nisummary_object, nif_object, parent=None):
        super().__init__(parent)

        self.NIf = nif_object
        self.NISummary = nisummary_object
        self.abut = []
        self.bbut = []

        layout = QtWidgets.QVBoxLayout(self)

        for i in range(4):
            layout.addWidget(QtWidgets.QLabel(self.NIf.channelnames[i]))

            row_widget = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row_widget)
            layout.addWidget(row_widget)

            label_a = QtWidgets.QLabel("a")
            row_layout.addWidget(label_a)

            nb_a = QtWidgets.QDoubleSpinBox()
            nb_a.setMinimum(0)
            nb_a.setMaximum(2)
            nb_a.setSingleStep(0.05)
            nb_a.setValue(self.NIf.a[i])
            nb_a.valueChanged.connect(partial(self.set_a, channel=i))
            row_layout.addWidget(nb_a)
            self.abut.append(nb_a)

            label_b = QtWidgets.QLabel("b")
            row_layout.addWidget(label_b)

            nb_b = QtWidgets.QDoubleSpinBox()
            nb_b.setSingleStep(0.05)
            nb_b.setValue(self.NIf.b[i])
            nb_b.valueChanged.connect(partial(self.set_b, channel=i))
            row_layout.addWidget(nb_b)
            self.bbut.append(nb_b)

        save_button = QtWidgets.QPushButton("Save channels to file")
        save_button.clicked.connect(self.NIf.save_coeff_to_file)
        layout.addWidget(save_button)

        recalc_button = QtWidgets.QPushButton("Recalculate channels from visible data")
        recalc_button.clicked.connect(self.auto_calculate_coeffs_from_visible)
        layout.addWidget(recalc_button)

        # Anisotropy center controls
        layout.addSpacing(10)
        layout.addWidget(QtWidgets.QLabel("Anisotropy center:"))

        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QHBoxLayout(center_widget)
        layout.addWidget(center_widget)

        center_layout.addWidget(QtWidgets.QLabel("X"))
        self.aniso_x = QtWidgets.QDoubleSpinBox()
        self.aniso_x.setMinimum(-1.0)
        self.aniso_x.setMaximum(1.0)
        self.aniso_x.setSingleStep(0.01)
        self.aniso_x.setValue(self.NIf.anisotropy_center[0])
        self.aniso_x.valueChanged.connect(self.set_anisotropy_x)
        center_layout.addWidget(self.aniso_x)

        center_layout.addWidget(QtWidgets.QLabel("Y"))
        self.aniso_y = QtWidgets.QDoubleSpinBox()
        self.aniso_y.setMinimum(-1.0)
        self.aniso_y.setMaximum(1.0)
        self.aniso_y.setSingleStep(0.01)
        self.aniso_y.setValue(self.NIf.anisotropy_center[1])
        self.aniso_y.valueChanged.connect(self.set_anisotropy_y)
        center_layout.addWidget(self.aniso_y)

        # Buttons
        layout.addSpacing(10)

        save_button = QtWidgets.QPushButton("Save anisotropy to file")
        save_button.clicked.connect(self.NIf.save_anisotropy_to_file)
        layout.addWidget(save_button)

        recalc_button = QtWidgets.QPushButton(
            "Recalculate anisotropy from visible data"
        )
        recalc_button.clicked.connect(self.auto_calculate_anisotropy_from_visible)
        layout.addWidget(recalc_button)

    # --- Handlers ---

    def auto_calculate_anisotropy_from_visible(self):
        self.NIf.auto_calculate_anisotropy_from_visible()
        self.aniso_x.setValue(self.NIf.anisotropy_center[0])
        self.aniso_y.setValue(self.NIf.anisotropy_center[1])

    def auto_calculate_coeffs_from_visible(self):
        self.NIf.auto_calculate_coeffs_from_visible()
        for i, nb in enumerate(self.abut):
            nb.blockSignals(True)
            nb.setValue(self.NIf.a[i])
            nb.blockSignals(False)
        self.NISummary.update_loaded_file(force=True)

    def set_a(self, value, channel):
        self.NIf.a[channel] = value
        self.NISummary.update_loaded_file(force=True)

    def set_b(self, value, channel):
        self.NIf.b[channel] = value
        self.NISummary.update_loaded_file(force=True)

    def set_anisotropy_x(self, value):
        self.NIf.anisotropy_center[0] = value
        self.NISummary.display_anisotropy()

    def set_anisotropy_y(self, value):
        self.NIf.anisotropy_center[1] = value
        self.NISummary.display_anisotropy()
