import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import os
from pymeasure.log import console_log
from pymeasure.display.Qt import QtCore, QtGui, fromUi
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, unique_filename
from SS9Procedure import SS9Procedure

import numpy as np

class SS9GUI(ManagedWindow):

    def __init__(self):
        super(SS9GUI, self).__init__(
            procedure_class=SS9Procedure,
            displays=[
                'your_name',
                'field_strength',
                'delay',
                'T_max',
                'num_averages',
                'mm1_measurement',
                'mm1_range',
                'mm1_address',
                'mm2_measurement',
                'mm2_range',
                'mm2_address',
                'mm3_measurement',
                'mm3_range',
                'mm3_address',
                'mm4_measurement',
                'mm4_range',
                'mm4_address',
                ],
            x_axis='elapsed_time',
            y_axis='T'
        )
        self.setWindowTitle('PyMeasure SS9 Lab')

    def _setup_ui(self):
        """
        Loads custom QT UI for daedalus STFMR measurements
        """
        super(SS9GUI, self)._setup_ui()
        self.inputs.hide()
        self.run_directory = os.path.dirname(os.path.realpath(__file__))
        self.inputs = fromUi(os.path.join(self.run_directory,'SS9_gui.ui'))

    def make_procedure(self):
        """
        Constructs a single procedure
        """
        procedure = SS9Procedure()
        procedure.your_name = self.inputs.your_name.text()
        procedure.field_strength = self.inputs.field_strength.value()
        procedure.delay = self.inputs.delay.value() #s
        procedure.T_max = self.inputs.T_max.value() #K
        procedure.num_averages = self.inputs.num_averages.value()

        procedure.mm1_measurement = [True,False][self.inputs.mm1_measurement.currentIndex()]
        procedure.mm1_range = [0.1, 1, 10][self.inputs.mm1_range.currentIndex()]
        procedure.mm1_address = self.inputs.mm1_address.text()

        procedure.mm2_measurement = [True,False][self.inputs.mm2_measurement.currentIndex()]
        procedure.mm2_range = [0.1, 1, 10][self.inputs.mm2_range.currentIndex()]
        procedure.mm2_address = self.inputs.mm2_address.text()

        procedure.mm3_measurement = [True,False][self.inputs.mm3_measurement.currentIndex()]
        procedure.mm3_range = [0.1, 1, 10][self.inputs.mm3_range.currentIndex()]
        procedure.mm3_address = self.inputs.mm3_address.text()

        procedure.mm4_measurement = [True,False][self.inputs.mm4_measurement.currentIndex()]
        procedure.mm4_range = [0.1, 1, 10][self.inputs.mm4_range.currentIndex()]
        procedure.mm4_address = self.inputs.mm4_address.text()

        return procedure

    def queue(self):
        direc = self.inputs.save_dir.text()
        # create list of procedures to run
        procedure = self.make_procedure()

        # create files
        pre = (procedure.your_name + '_') if procedure.your_name else ''
        suf = 'SS9'
        filename = unique_filename(direc,dated_folder=True,suffix=suf,
                                   prefix=pre)
        # ensure *some* sample name exists so Results.load() works
        if procedure.your_name == '':
            procedure.your_name = 'undefined'

        # Queue experiment
        results = Results(procedure,filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = SS9GUI()
    window.show()
    sys.exit(app.exec_())
