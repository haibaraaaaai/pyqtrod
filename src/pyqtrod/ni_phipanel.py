from PyQt6 import QtWidgets
from functools import partial


class PhiPanel(QtWidgets.QWidget):
    def __init__(self, nisummary_object, nif_object, parent=None):
        super().__init__(parent)

        self.NIf = nif_object
        self.NISummary = nisummary_object
        self.abut = []
        self.bbut = []

        layout = QtWidgets.QVBoxLayout(self)

        # Double SpinBox for start time
        self.start_time_spinbox = QtWidgets.QDoubleSpinBox()
        self.start_time_spinbox.setMinimum(0.0)
        self.start_time_spinbox.setMaximum(float("inf"))
        self.start_time_spinbox.setValue(0.0)
        self.start_time_spinbox.setPrefix("Start time: ")
        layout.addWidget(self.start_time_spinbox)

        # Double SpinBox for stop time
        self.stop_time_spinbox = QtWidgets.QDoubleSpinBox()
        self.stop_time_spinbox.setMinimum(0.0)
        self.stop_time_spinbox.setMaximum(float("inf"))
        self.stop_time_spinbox.setValue((self.NIf.datasize - 1) / self.NIf.freq)
        self.stop_time_spinbox.setPrefix("Stop time: ")
        layout.addWidget(self.stop_time_spinbox)

        # Checkbox for average_before
        self.average_before_checkbox = QtWidgets.QCheckBox("Average Before Computation")
        layout.addWidget(self.average_before_checkbox)

        # Integer SpinBox for average_before_window
        self.average_before_window_spinbox = QtWidgets.QSpinBox()
        self.average_before_window_spinbox.setMinimum(1)
        self.average_before_window_spinbox.setMaximum(100)
        self.average_before_window_spinbox.setValue(1)
        self.average_before_window_spinbox.setPrefix("Averaging window: ")
        layout.addWidget(self.average_before_window_spinbox)

        # Integer SpinBox for average_before_dec
        self.average_before_dec_spinbox = QtWidgets.QSpinBox()
        self.average_before_dec_spinbox.setMinimum(1)
        self.average_before_dec_spinbox.setMaximum(10000)
        self.average_before_dec_spinbox.setValue(1)
        self.average_before_dec_spinbox.setPrefix("Decimation after averaging: ")
        layout.addWidget(self.average_before_dec_spinbox)
        # Create three buttons
        self.button2 = QtWidgets.QPushButton("Compute Anisotropy Phi")
        self.button3 = QtWidgets.QPushButton("Save Phi to File")

        # Add buttons to the layout
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)

        # Connect buttons to actions (replace 'action1', 'action2', 'action3' with your method names)
        self.button2.clicked.connect(self.compute_anisotropy_phi)
        self.button3.clicked.connect(self.save_phi_to_file)

    # --- Handlers ---

    def compute_anisotropy_phi(self):
        self.NISummary.plot_phi_anisotropy(
            start=int(self.start_time_spinbox.value() * self.NIf.freq),
            stop=int(self.stop_time_spinbox.value() * self.NIf.freq),
            average_before=self.average_before_checkbox.isChecked(),
            average_before_window=self.average_before_window_spinbox.value(),
            average_before_dec=self.average_before_dec_spinbox.value(),
        )

    def save_phi_to_file(self):
        default_path = self.NIf.path.rsplit(".", 1)[0] + "_phiu.npy"
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Phi Data", default_path, "NumPy Files (*.npy);;All Files (*)"
        )
        if filename:
            self.NISummary.save_phi_to_file(filename)
        pass
