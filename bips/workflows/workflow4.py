from base import MetaWorkflow, load_json
from enthought.traits.api import HasTraits, Directory, Bool, Button
import enthought.traits.api as traits
from enthought.traits.ui.api import Handler, View, Item, UItem, HGroup, Group
from traitsui.menu import OKButton, CancelButton
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
desc = """
Test Freesurfer workflow
=======================================
Grab data
Freesurfer source
Convert brainmask.mgz to brainmask.nii.gz
Convert brainmask.nii.gz to brainmask.mgz
DataSink 
"""

mwf = MetaWorkflow()
mwf.inputs.uuid = '4ba509108afb11e18b5e001e4fb1404c'
mwf.tags = ['TEST','Freesurfer']

# Define Config
from workflow1 import config_ui

# Define workflow
import nipype.interfaces.freesurfer as fs
from nipype.interfaces.io import FreeSurferSource

def test_fs(name='test_fs'):

    workflow = pe.Workflow(name=name)
    
    # Define Nodes
    inputspec = pe.Node(interface=util.IdentityInterface(fields=['subject_id', 'sd']), name='inputspec')
    
    fssource = pe.Node(interface = FreeSurferSource(),name='fssource')
    
    convert1 = pe.Node(interface=fs.MRIConvert(),name='converter1')
    
    convert2 = pe.Node(interface=fs.MRIConvert(),name='converter2')
    
    convert1.inputs.out_type = 'niigz'
    convert1.inputs.in_type = 'mgz'
    
    convert2.inputs.out_type = 'mgz'
    convert2.inputs.in_type = 'niigz'
    
    outputspec = pe.Node(interface=util.IdentityInterface(fields=['outfile']), name='outputspec')
    
    # Connect Nodes
    workflow.connect(inputspec,'subject_id',fssource,'subject_id')
    workflow.connect(inputspec,'sd',fssource,'subjects_dir')
    
    workflow.connect(fssource, 'brainmask', convert1, 'in_file')
    workflow.connect(convert1, 'out_file', convert2, 'in_file')
    workflow.connect(convert2, 'out_file', outputspec, 'outfile')
    
    return workflow
    
def main(config):
    c = load_json(config)
    wk = test_fs()
    wk.base_dir = c["working_dir"]
    wk.inputs.inputspec.subject_id = c["subjects"].split(',')[0]
    wk.inputs.inputspec.sd = c["surf_dir"]
    sinker = pe.Node(nio.DataSink(), name='sinker')
    sinker.inputs.base_directory = c["sink_dir"]
    sinker.inputs.container = c["subjects"].split(',')[0]
    out = wk.get_node('outputspec')
    wk.connect(out, 'outfile', sinker, 'test_fs.result')
    wk.config = {'execution' : {'crashdump_dir' : c["crash_dir"]}}
    if c["run_on_grid"]:
        wk.run(plugin=c["plugin"],plugin_args=c["plugin_args"])
    else:
        wk.run()
    
mwf.inputs.workflow_main_function = main        
mwf.inputs.config_ui = lambda : config_ui
mwf.inputs.config_view = View(Group(Item(name='working_dir'),
             Item(name='sink_dir'),
             Item(name='crash_dir'),
             Item(name='surf_dir'),
             label='Directories',show_border=True),
             Group(Item(name='run_on_grid'),
             Item(name='plugin',enabled_when="run_on_grid"),
             Item(name='plugin_args',enabled_when="run_on_grid"),
             Item(name='test_mode'),
             label='Execution Options',show_border=True),
             Group(Item(name='subjects'),
             label='Subjects',show_border=True),
             buttons = [OKButton, CancelButton],
             resizable=True,
             width=1050)
    
