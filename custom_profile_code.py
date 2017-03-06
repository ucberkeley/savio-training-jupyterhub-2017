#import uuid
#c.BaseParallelApplication.cluster_id = str(uuid.uuid4())  # this would create a unique ID
c.IPClusterStart.controller_launcher_class = 'SlurmControllerLauncher'
c.IPClusterEngines.engine_launcher_class = 'SlurmEngineSetLauncher'
c.IPClusterEngines.n = 48   # 2 nodes worth of engines...
c.SlurmLauncher.queue = 'savio2'
c.SlurmLauncher.account = 'fc_paciorek'  # your FCA or condo here
c.SlurmLauncher.qos = 'savio_normal'
c.SlurmLauncher.timelimit = '8:0:0'
#c.SlurmLauncher.options = '--export=ALL --mem=10g'
c.SlurmControllerLauncher.batch_template = '''#!/bin/bash -l
#SBATCH --job-name=ipcontroller-fake
#SBATCH --partition={queue}
#SBATCH --account={account}
#SBATCH --qos={qos}
#SBATCH --ntasks=1
#SBATCH --time={timelimit}
'''
c.SlurmEngineSetLauncher.batch_template = '''#!/bin/bash -l
#SBATCH --job-name=ipcluster-{cluster_id}
#SBATCH --partition={queue}
#SBATCH --account={account}
#SBATCH --qos={qos}
#SBATCH --ntasks={n}
#SBATCH --time={timelimit}

/global/software/sl-6.x86_64/modules/langs/python/3.5.1/bin/ipcontroller --profile-dir={profile_dir} --cluster-id="{cluster_id}" & sleep 10
srun /global/software/sl-6.x86_64/modules/langs/python/3.5.1/bin/ipengine --profile-dir={profile_dir} --cluster-id="{cluster_id}"
'''
# for Python 2.7.8, replace the last two lines with:
# module load python/2.7.8 ipython
# ipcontroller --profile-dir={profile_dir} --cluster-id="{cluster_id}" & sleep 10
# ipengine --profile-dir={profile_dir} --cluster-id="{cluster_id}"
