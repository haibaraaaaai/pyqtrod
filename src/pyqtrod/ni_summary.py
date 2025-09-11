# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from functools import partial
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkColor

import numpy as np

from importlib import import_module, reload
import importlib.resources
import inspect
import importlib.resources as pkg_resources

from .ni_correctionpanel import CorrectionPanel
from .ni_phipanel import PhiPanel
from .module_dialog import ModuleDialog
from .matrix_dialog import MatrixDialog, MatrixChoose

from pynavgui import PngPlotRegionGrid


modules_root = "pyqtrod.modules"


class NISummary(QtWidgets.QMainWindow):
    def __init__(self, NIf, threadpool, png_instance=None):
        super(NISummary, self).__init__()
        self.NIf = NIf
        self.png_instance = png_instance
        self.threadpool = threadpool
        with pkg_resources.path("pyqtrod", "ni_summary.ui") as ui_path:
            uic.loadUi(ui_path, self)
        self.create_main_widget()
        self.init_plot_main()

        self.set_file_properties()
        self.decimatebox.setCurrentText(str(self.NIf.dec))
        self.set_pol_decim_buttons()
        self.init_load_as_seen()
        self.display_anisotropy()
        self.display_trajectory()
        # self.setslider()
        self.n_modules = 0
        # self.set_coeffs_buttons()
        self.toolmodules = []

        self.imported_modules = []
        # # Install event filter
        self.installEventFilter(self)
        self.set_memory_text()
        # self.load_all_modules()
        self.phi_plot = None

    def create_main_widget(self):
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Top panel
        self.plot_widget = PngPlotRegionGrid(png_instance=self.png_instance)
        self.main_layout.addWidget(self.plot_widget)

        # Bottom container with two GL views
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.anisotropy_gl = gl.GLViewWidget()
        self.anisotropy_gl.setBackgroundColor("k")
        self.anisotropy_gl.setWindowTitle("3D plot - Anisotropy")
        self.anisotropy_gl.setCameraPosition(distance=40)

        self.trajectory_gl = gl.GLViewWidget()
        self.trajectory_gl.setBackgroundColor("k")

        # Add to layout
        self.right_layout.addWidget(self.anisotropy_gl)
        self.right_layout.addWidget(self.trajectory_gl)

        total_width = self.main_widget.width()
        total_height = self.main_widget.height()
        widget_width = min(total_height // 2, total_width // 3)
        self.right_widget.setFixedWidth(widget_width)
        self.right_widget.setFixedHeight(2 * widget_width)

        # Add right container to main layout
        self.main_layout.addWidget(self.right_widget)

    def display_anisotropy(self):

        c0, c90, c45, c135 = self.NIf.ret_cor_channel()
        Itot = c0 + c90 + c45 + c135
        I0 = (c0 - c90) / Itot - self.NIf.anisotropy_center[0]
        I1 = (c45 - c135) / Itot - self.NIf.anisotropy_center[1]

        self.v1 = np.column_stack((I0, I1, np.zeros(len(I0))))

        plt = gl.GLScatterPlotItem(
            pos=self.v1, size=0.01, pxMode=False, color=mkColor("red")
        )
        big_point = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]), size=0.1, pxMode=False, color=mkColor("white")
        )
        plt.setGLOptions("translucent")
        self.anisotropy_gl.clear()
        self.anisotropy_gl.addItem(plt)
        self.anisotropy_gl.addItem(big_point)
        self.anisotropy_gl.show()

    def display_trajectory(self):
        (phi, theta1) = self.NIf.ret_all_var(phiraw=True)
        v1 = np.column_stack(
            (
                np.sin(theta1) * np.cos(phi),
                np.sin(theta1) * np.sin(phi),
                np.cos(theta1),
            )
        )
        # v2 = np.array([np.sin(theta0)*np.cos(phi0),np.sin(theta0)*np.sin(phi0),np.cos(theta0)])
        # fac = v1.transpose().dot(v2)
        # Itot = Itots2thet / np.sin(theta1)**2
        v1[np.isnan(v1)] = 0
        plt = gl.GLScatterPlotItem(
            pos=v1, size=0.01, pxMode=False, color=mkColor("red")
        )
        print(v1)
        plt.setGLOptions("translucent")
        self.trajectory_gl.clear()
        self.trajectory_gl.addItem(plt)
        self.trajectory_gl.show()

    def resizeEvent(self, event):
        self.update_gl_sizes()
        return super().resizeEvent(event)

    def update_gl_sizes(self):
        total_width = self.main_widget.width()
        total_height = self.main_widget.height()
        widget_width = min(total_height // 2, total_width // 3)
        self.right_widget.setFixedWidth(widget_width)
        self.right_widget.setFixedHeight(2 * widget_width)

    def load_all_modules(self):
        with importlib.resources.path(modules_root, "") as modules_path:
            fl = [
                f.stem
                for f in modules_path.iterdir()
                if (
                    f.is_file()
                    and f.as_posix().endswith(".py")
                    and not f.as_posix().endswith("__.py")
                )
            ]
        fl2 = []
        print("Modules found:", fl)
        for f in fl:
            if not f.endswith("beta.py"):
                if "anis_traj_gl" in f:
                    fl2.append(f)
        for t in fl2:
            self.load_module(t)

    def load_module_menu(self):
        with importlib.resources.path(modules_root, "") as modules_path:
            fl = [
                f.stem
                for f in modules_path.iterdir()
                if (
                    f.is_file()
                    and f.as_posix().endswith(".py")
                    and not f.as_posix().endswith("__.py")
                )
            ]
        fl2 = []
        for f in fl:
            fl2.append(f)
        dialog = ModuleDialog("Module Dialog", stringlist=fl2)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            list_selected_modules = dialog.get_selected_modules()
        else:
            return
        for t in list_selected_modules:
            self.load_module(t)

    def open_correction_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Correction des coefficients")
        dialog.setModal(False)  # bloque l’interface tant qu’ouvert

        layout = QtWidgets.QVBoxLayout(dialog)
        panel = CorrectionPanel(nisummary_object=self, nif_object=self.NIf)
        layout.addWidget(panel)

        dialog.resize(400, 300)
        dialog.exec()  # Ouvre le QDialog modale

    def open_phi_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Phi correction")
        dialog.setModal(False)
        layout = QtWidgets.QVBoxLayout(dialog)
        panel = PhiPanel(nisummary_object=self, nif_object=self.NIf)
        layout.addWidget(panel)
        dialog.resize(400, 300)
        dialog.exec()

    def edit_matrix_menu(self):
        dialog = MatrixDialog("Edit correction matrix", mat=self.NIf.matcor)
        dialog.exec()
        self.NIf.update_data_from_file(time=-2)
        self.NIv.update_series_from_file()

    def choose_matrix_menu(self):
        dialog = MatrixChoose("Choose correction matrix", file=self.NIf)
        dialog.exec()
        self.NIf.update_data_from_file(time=-2)
        self.NIv.update_series_from_file()

    def load_module(self, module):  # load or reload
        def get_class_from_module(module):
            classes = [
                member
                for member in inspect.getmembers(module, inspect.isclass)
                if member[1].__module__ == module.__name__
            ]
            if len(classes) == 1:
                return classes[0][1]  # Returns the name of the class
            elif len(classes) > 1:
                raise ValueError("Module contains more than one class.")
            else:
                raise ValueError("No classes found in the module.")

        module_name = f"{modules_root}.{module}"
        found = 0
        for i in range(len(self.imported_modules)):
            m, mn = self.imported_modules[i]
            if mn == module_name:
                found = 1
                module = reload(m)
                self.imported_modules[i][0] = module
                break
        if found == 0:
            module = import_module(module_name)
            self.imported_modules.append([module, module_name])
        try:
            # Try to get the class object from the module
            class_obj = get_class_from_module(module)

            # Create an instance of the class
            instance = class_obj(self)
            print("Created instance:", instance)
        except ValueError as e:
            print(f"Error: {e}")

    def add_tool_widget(self, widget, name):
        if self.toolmodules == []:
            self.toolbox = QtWidgets.QToolBox()
            self.dockanalysis.setWidget(self.toolbox)
        else:
            for i in range(len(self.toolmodules)):
                w, n, ind = self.toolmodules[i]
                if n == name:
                    del self.toolmodules[i]
                    # w.hide()
                    self.toolbox.removeItem(ind)
                    for j in range(len(self.toolmodules)):
                        w2, n2, ind2 = self.toolmodules[j]
                        if ind2 >= ind:
                            self.toolmodules[j][2] -= 1
                    break
        ind = self.toolbox.addItem(widget, name)
        self.toolmodules.append([widget, name, ind])

    def init_plot_main(self):
        self.colors_plot_main = ["r", "g", "b", "orange"]
        for i in range(len(self.NIf._channels)):
            if i == 0:
                self.plotmain = self.plot(
                    self.NIf.xs,
                    self.NIf.data[i],
                    xtitle="Time (s)",
                    ytitle="APD Voltage (V)",
                    plotname="APD signals",
                    no_quit=True,
                    name=f"""{self.NIf.channelnames[0]}
                    ({self.NIf.orientations[0]}°)""",
                    pen=self.colors_plot_main[i],
                )
            else:
                self.plotmain.add_ds(
                    self.NIf.xs,
                    self.NIf.data[i],
                    name=f"""{self.NIf.channelnames[i]}
                    ({self.NIf.orientations[i]}°)""",
                    pen=self.colors_plot_main[i],
                )

    def update_plot_main(self):
        self.plotmain.clear()
        for i in range(len(self.NIf._channels)):
            self.plotmain.add_ds(
                self.NIf.xs,
                self.NIf.data[i],
                name=f"""{self.NIf.channelnames[i]}
                    ({self.NIf.orientations[i]}°)""",
                pen=self.colors_plot_main[i],
            )

    def get_visible_pol_channels(self):
        xa, xb = self.plotmain.viewRange()[0]
        c0, c90, c45, c135 = self.NIf.ret_cor_channel(xa, xb)
        return c0, c90, c45, c135

    def get_visible_pol_channels_raw(self):  # return raw and decimated
        xa, xb = self.plotmain.viewRange()[0]
        c0, c90, c45, c135 = self.NIf.ret_raw_channel(xa, xb)
        return c0, c90, c45, c135

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.key() in [QtCore.Qt.Key.Key_Right, QtCore.Qt.Key.Key_Left]:
            if self.load_as_seen:
                self.update_loaded_file()
        (a, b) = self.plotmain.viewRange()[0]
        # self.DataSlider.setValue((a, b))

    # def eventFilter(self, source, event):
    #     if event.type() == QtCore.QEvent.KeyRelease:
    #         # Handle the key event here

    #         if event.key() in [QtCore.Qt.Key.Key_Right, QtCore.Qt.Key.Key_Left]:
    #             if self.load_as_seen:
    #                 self.update_loaded_file()
    #     return super().eventFilter(source, event)

    def set_file_properties(self):
        self.filepathdisplay.setText(self.NIf.path)
        self.groupnbdisplay.setText(str(self.NIf.groupnb))
        self.freqdisplay.setText(str(round(self.NIf.freq / 1000)))
        self.startTimedisplay.setDateTime(
            QtCore.QDateTime.fromSecsSinceEpoch(
                int(self.NIf.starttime.astype("int") / 1e6)
            )
        )  # trick will need to correct that if dates become incorrect
        self.lengthptsdisplay.setText("{:.3e}".format(self.NIf.datasize))
        self.lengthmindisplay.setText(
            "{:.2f}".format(self.NIf.datasize / self.NIf.freq / 60)
        )

        pass

    def set_pol_decim_buttons(self):

        self.start_load_in_mem.setValue(self.NIf.xminmem)
        self.stop_load_in_mem.setValue(self.NIf.xmaxmem)
        self.stop_load_in_mem.setMaximum(self.NIf.datasize / self.NIf.freq)
        self.stop_load_in_mem.valueChanged.connect(self.start_load_in_mem.setMaximum)
        self.start_load_in_mem.setMaximum(self.stop_load_in_mem.value())
        self.decimatebox.currentTextChanged.connect(lambda: self.indicate_loaded_size())
        self.decimatebox.currentTextChanged.connect(
            lambda: self.update_loaded_file(force=True)
        )
        self.max_size.setValue(self.NIf.max_size)
        self.max_size.valueChanged.connect(lambda: self.update_loaded_file(force=True))
        self.stop_load_in_mem.valueChanged.connect(lambda: self.indicate_loaded_size())
        self.start_load_in_mem.valueChanged.connect(lambda: self.indicate_loaded_size())
        self.decimation_averaged.setChecked(self.NIf.dec_average)
        self.decimation_averaged.stateChanged.connect(self.set_dec_average)

        self.button_load_as_seen.stateChanged.connect(self.set_load_as_seen)

        # self.DataSlider.setValue((self.NIf.xminmem, self.NIf.xmaxmem))

        self.loadinmem.clicked.connect(self.update_loaded_file)

    def set_dec_average(self, value):
        self.NIf.dec_average = bool(value)
        self.update_loaded_file()

    def init_load_as_seen(self):
        self.button_load_as_seen.setChecked(True)
        self.set_load_as_seen(True)

    def set_load_as_seen(self, state):
        if state == 0:
            self.load_as_seen = False
            self.NIf.max_size = int(1e9)
        else:
            self.load_as_seen = True
            self.NIf.max_size = int(self.max_size.value())
            self.NIf.init_data_share(
                int(self.decimatebox.currentText()),
                timestart=self.start_load_in_mem.value(),
                timestop=self.stop_load_in_mem.value(),
            )
            self.update_plot_main()
        self.loadinmem.setEnabled(not self.load_as_seen)

    def indicate_loaded_size(self):
        self.nb_points_to_load_in_mem.setWordWrap(True)
        nb_points = int(
            self.NIf.freq
            * (self.stop_load_in_mem.value() - self.start_load_in_mem.value())
            / int(self.decimatebox.currentText())
        )
        memory = 4 * self.NIf.data.dtype.itemsize * nb_points / 1e6
        self.nb_points_to_load_in_mem.setText(
            f"Corresponding to roughly {nb_points} points and {memory} MB of memory."
        )

    def update_loaded_file(self, force=False):
        if self.load_as_seen is False:
            timestart = self.start_load_in_mem.value()
            timestop = self.stop_load_in_mem.value()
            dec = int(self.decimatebox.currentText())
            self.NIf.init_data_share(
                dec,
                timestart=timestart,
                timestop=timestop,
            )
            # self.DataSlider.setValue((self.NIf.xminmem, self.NIf.xmaxmem))
            self.update_plot_main()
        else:
            (a, b) = self.plotmain.viewRange()[0]
            # self.DataSlider.setValue((a, b))
            dec = int(self.decimatebox.currentText())
            center = 0.5 * a + 0.5 * b
            memintime = self.max_size.value() / self.NIf.freq * dec
            max_size = int(self.max_size.value())

            if self.NIf.dec != dec:
                self.NIf.init_data_share(
                    dec,
                    timestart=center - memintime,
                    timestop=center + memintime,
                )
                self.update_plot_main()
            if max_size != self.NIf.max_size:
                self.NIf.max_size = max_size
                self.NIf.init_data_share(
                    dec,
                    timestart=center - memintime,
                    timestop=center + memintime,
                )
                self.update_plot_main()

            else:
                if force or (b > self.NIf.xmaxmem) or (a < self.NIf.xminmem):
                    self.NIf.update_data_from_file(time=0.5 * a + 0.5 * b)
                    self.update_plot_main()
                (a, b) = self.plotmain.viewRange()[0]
            # self.DataSlider.setValue((a, b))
        self.display_anisotropy()
        self.display_trajectory()

        self.set_memory_text()

    def set_memory_text(self):
        self.info_data_loaded.setText(
            f""" NOW IN MEMORY: <b style="color:Tomato;">Decimation</b> : {self.NIf.dec_in_mem} \n
  <b style="color:Tomato;">Averaged</b> : {self.NIf.dec_average_in_mem} \n 
    <b style="color:Tomato;">Loaded from</b> : {round(self.NIf.xminmem,2)} s \n
  <b style="color:Tomato;">Loaded to</b> : {round(self.NIf.xmaxmem,2)} s
"""
        )

    def setslider(
        self,
    ):
        self.DataSlider.setMinimum(0)
        self.DataSlider.setMaximum(self.NIf.datasize / self.NIf.freq)
        # self.DataSlider.setHandleLabelPosition(LabelPosition.NoLabel)
        self.DataSlider.valueChanged.connect(self.sliderchanged)

    def sliderchanged(self, value):
        return
        self.plotmain.setXRange(value[0], value[1])

    def get_current_active_widget(self):
        ac_subwindow = self.mdiArea.activeSubWindow()
        cw = ac_subwindow.widget()
        return cw

    def plot(self, x, y, title="", xtitle="", ytitle="", no_quit=False, **kwargs):

        ph = self.plot_widget.addPlot(x=x, y=y, xtitle=xtitle, ytitle=ytitle, **kwargs)
        self.plot_widget.show()
        return ph

    def plot_phi_anisotropy(
        self,
        start=0,
        stop=None,
        cutwindow=1000000,
        average_before=0,
        average_before_window=1,
        average_before_dec=1,
    ):
        if self.plotmain is None:
            return
        if self.phi_plot is None:
            plotregion = self.plotmain.parentplotregion
            self.phi_plot = plotregion.add_plot(
                plotname="Phi", xtitle="Time (s)", ytitle="Phi (degrees)"
            )
        olddec = self.NIf.dec
        self.NIf.dec = 1
        self.phi = self.NIf.ret_phi(
            start,
            stop,
            raw=1,
            init=1,
            cutwindow=cutwindow,
            force_ref=0,
            average_before=average_before,
            average_before_window=average_before_window,
            average_before_dec=average_before_dec,
            no_anisotropy=False,
        )
        self.NIf.dec = olddec

        self.xs = (
            start / self.NIf.freq
            + np.arange(len(self.phi)) / self.NIf.freq * average_before_dec
        )
        self.phi_plot.clear()
        self.phi_plot.add_ds(
            self.xs,
            self.phi * 180 / np.pi,
            name="Phi",
        )
        return

    def save_phi_to_file(self, output_file):
        np.save(output_file, np.array([self.xs, self.phi]))

    def plot3D2D(self, title="", xtitle="", ytitle=""):
        winpg = QtWidgets.QMdiSubWindow()
        winpg.setWindowTitle(title)
        widget = QtWidgets.QWidget()
        winpg.setWidget(widget)
        self.mdiArea.addSubWindow(winpg)
        w = gl.GLViewWidget()
        w.setBackgroundColor("k")
        w.setWindowTitle(title)
        w.setCameraPosition(distance=40)
        layoutgb = QtWidgets.QGridLayout()
        widget.setLayout(layoutgb)
        ploth = pg.PlotWidget(title=title)
        ploth.enableAutoRange(True, True)
        layoutgb.addWidget(w, 0, 0)
        layoutgb.addWidget(ploth, 0, 1)
        winpg.show()
        winpg.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        ploth.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        w.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        w.setSizePolicy(ploth.sizePolicy())
        return winpg, w, ploth
