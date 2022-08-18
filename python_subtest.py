import tempfile
from openmc.mpi import comm

def run(model):
    if comm.rank == 0:
        temp_dir = tempfile.TemporaryDirectory()
        model.settings.output = {'path': temp_dir.name,
                                 'summary': True,
                                 'tallies': False}
    else:
        temp_dir = None
    temp_dir = comm.bcast(temp_dir, root=0)
    run_kwargs = {'cwd': temp_dir.name}
    model.init_lib(intracomm=comm)
    statepoint_path = model.run(**run_kwargs)
    
