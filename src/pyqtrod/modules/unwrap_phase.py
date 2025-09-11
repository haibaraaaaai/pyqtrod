# This Python file uses the following encoding: utf-8
from PyQt6 import QtWidgets, uic
import numpy as np
import pywt
from ..pyqtworker import PyQtWorker
from ..helpers import extract_phase
from pyqtgraph import mkColor
import pyqtgraph.opengl as gl
import importlib

importlib.reload(extract_phase)
compute_reference_trace = extract_phase.compute_reference_trace
func_unwrap_phase = extract_phase.unwrap_phase

import importlib.resources as pkg_resources


class UnwrapPhase(QtWidgets.QWidget):
    def __init__(self, NITab=None, NIfile=None, threadpool=None):
        super(QtWidgets.QWidget, self).__init__()
        with pkg_resources.path("pyqtrod.modules", "unwrap_phase.ui") as ui_path:
            uic.loadUi(ui_path, self)

        if NITab is not None:
            self.NITab = NITab
            self.NIf = NITab.NIf
            self.threadpool = NITab.threadpool
        elif NIfile is not None and threadpool is not None:
            self.NIf = NIfile
            self.threadpool = threadpool
        else:
            raise ImportError("cannot initialize without file and threadpool")

        self.startstopbutton.pressed.connect(self.set_start_stop_visible)

        self.windowsize = 100
        self.preconvolutionwindow.setValue(self.windowsize)
        self.preconvolutionwindow.valueChanged.connect(self.set_convolutionwindowsize)

        self.periodstart = 0
        self.periodstartbox.setValue(self.periodstart)
        self.periodstartbox.valueChanged.connect(self.set_periodstart)

        self.periodend = 0.001
        self.periodendbox.setValue(self.periodend)
        self.periodendbox.valueChanged.connect(self.set_periodend)

        self.referencepoints = 200
        self.referencepointsbox.setValue(self.referencepoints)
        self.referencepointsbox.valueChanged.connect(self.set_referencepoints)

        self.smoothing = 0.001
        self.smoothbox.setValue(self.smoothing)
        self.smoothbox.valueChanged.connect(self.set_smoothing)

        self.computereferencetracebutton.pressed.connect(self.compute_reference)

        self.update_reference = False
        self.updatereferencebox.stateChanged.connect(self.set_update_reference)

        self.unwrapto = self.NIf.datasize / self.NIf.freq
        self.unwraptobox.setValue(self.unwrapto)
        self.unwraptobox.valueChanged.connect(self.set_unwrap_to)

        self.unwrapphasebutton.setEnabled(False)
        self.unwrapphasebutton.pressed.connect(self.unwrap_phase)

        self.pcaphasebutton.setEnabled(False)
        self.pcaphasebutton.pressed.connect(self.show_pca_phase)

        self.pca_phase_choice_value = 0
        self.pcaphasechoice.currentIndexChanged.connect(self.set_pca_phase_choice)

        NITab.add_tool_widget(self, "UnwrapPhase")

    def unwrap_phase(self):
        signals = self.NIf.ret_cor_channel_in_file(
            int(self.periodstart * self.NIf.freq),
            int(self.unwrapto * self.NIf.freq),
            ordl=["0", "90", "45", "135"],
            average=False,
            average_window=100,
            dec=1,
        )
        X_pca = self.pca.transform(np.column_stack(signals))
        X_pca = X_pca[:, :3]
        X_pca = np.apply_along_axis(
            lambda m: np.convolve(
                m, np.ones(self.windowsize) / self.windowsize, mode="valid"
            ),
            axis=0,
            arr=X_pca,
        )
        self.phaseindex, self.phase = func_unwrap_phase(
            X_pca, self.reference, self.update_reference, 250000
        )

        self.xs = np.linspace(self.periodstart, self.unwrapto, len(self.phase))
        self.plotphase = self.NITab.plot(
            self.xs,
            self.phase,
            title="Phi",
            xtitle="Time (s)",
            ytitle="Rad ",
            pen=None,
            symbolPen="black",
            symbolSize=2,
            symbol="o",
            symbolBrush="black",
            xArrayLinSorted=True,
        )
        self.pcaphasebutton.setEnabled(True)
        self.X_pca = X_pca

    def show_pca_phase(self):
        self.plotphase = self.NITab.plot(
            self.xs,
            self.X_pca[:, self.pca_phase_choice_value],
            title=f"PCA {self.pca_phase_choice_value}",
            xtitle="Time (s)",
            pen=None,
            symbolPen="black",
            symbolSize=2,
            symbol="o",
            symbolBrush="black",
            xArrayLinSorted=True,
        )
        self.plotphase.add_ds(
            self.xs,
            self.reference[self.phaseindex, self.pca_phase_choice_value],
            pen=None,
            symbolPen="red",
            symbolSize=2,
            symbol="o",
            symbolBrush="red",
            xArrayLinSorted=True,
        )

    def set_pca_phase_choice(self, value):
        self.pca_phase_choice_value = value

    def compute_reference(self):
        signals = self.NIf.ret_cor_channel_in_file(
            int(self.periodstart * self.NIf.freq),
            int(self.periodend * self.NIf.freq),
            ordl=["0", "90", "45", "135"],
            average=False,
            average_window=100,
            dec=1,
        )
        signals = np.column_stack(signals)
        print(signals.shape)
        self.reference, self.pca = compute_reference_trace(
            signals,
            self.windowsize,
            self.referencepoints,
            self.smoothing,
        )
        self.unwrapphasebutton.setEnabled(True)

        self.winpg, self.w = self.NITab.plot3D(title="3D plot - Reference trace")
        X_PCA = self.pca.transform(signals)
        X_PCA = X_PCA[:, :3]

        color = mkColor("r")
        color.setAlphaF(0.1)
        self.plt = gl.GLScatterPlotItem(pos=X_PCA, size=0.1, pxMode=False, color=color)
        self.w.addItem(self.plt)

        color = mkColor("w")

        plt = gl.GLLinePlotItem(pos=self.reference, color=color, width=1)
        self.w.addItem(plt)
        self.unwrapto = self.periodstart + 0.1
        self.unwraptobox.setValue(self.unwrapto)
        self.unwraptobox.setMinimum(self.unwrapto)

    def set_start_stop_visible(self):
        (xa, xb) = self.NITab.plotmain.viewRange()[0]
        if xa < 0:
            xa = 0
        if xb > self.NIf.datasize / self.NIf.freq:
            xb = self.NIf.datasize / self.NIf.freq - 0.1

        self.periodstartbox.setValue(xa)
        self.periodendbox.setValue(xb)

        self.set_periodstart(xa)
        self.set_periodend(xb)

    def set_convolutionwindowsize(self, value):
        self.windowsize = value

    def set_periodstart(self, value):
        self.periodstart = value

    def set_periodend(self, value):
        self.periodend = value

    def set_referencepoints(self, value):
        self.referencepoints = value

    def set_smoothing(self, value):
        self.smoothing = value

    def set_update_reference(self, value):
        self.update_reference = value

    def set_unwrap_to(self, value):
        self.unwrapto = value
