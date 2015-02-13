import mne
from mne.datasets import sample

from mne.externals.six import string_types
from os import path as op
import numpy as np

from mne import pick_types, pick_info
from mne.io.pick import _has_kit_refs
from mne.io import read_info
from mne.io.constants import FIFF
# from .forward import Forward, write_forward_solution, _merge_meg_eeg_fwds
# from ._compute_forward import _compute_forwards
from mne.transforms import (invert_transform, transform_surface_to,
                          read_trans, _get_mri_head_t_from_trans_file,
                          apply_trans, _print_coord_trans, _coord_frame_name)
from mne.utils import logger, verbose
from mne.source_space import (read_source_spaces, _filter_source_spaces,
                            SourceSpaces)
from mne.surface import read_bem_solution, _normalize_vectors

data_path = sample.data_path()

ave_fname = data_path + '/MEG/sample/sample_audvis-ave.fif'
mri = data_path + '/MEG/sample/sample_audvis_raw-trans.fif'
bem = data_path + '/subjects/sample/bem/sample-5120-5120-5120-bem-sol.fif'
subjects_dir = data_path + '/subjects'

@verbose
def dipole_fit(evoked, mri, bem, tmin, tmax, origin=(0, 0, 40), meg=True, eeg=False,
               n_jobs=1, verbose=True):
    """XXX"""
    # Currently not (sup)ported:
    # 1. EEG Sphere model (not used much)
    # 2. --grad option (gradients of the field, not used much)
    # 3. --fixed option (can be computed post-hoc)
    # 4. --mricoord option (probably not necessary)

    # read the transformation from MRI to HEAD coordinates
    # (could also be HEAD to MRI)
    if isinstance(mri, string_types):
        if not op.isfile(mri):
            raise IOError('mri file "%s" not found' % mri)
        if op.splitext(mri)[1] in ['.fif', '.gz']:
            mri_head_t = read_trans(mri)
        else:
            mri_head_t = _get_mri_head_t_from_trans_file(mri)
    else:  # dict
        mri_head_t = mri
        mri = 'dict'

    info = evoked.info

    if not op.isfile(bem):
        raise IOError('BEM file "%s" not found' % bem)
    if not isinstance(info, (dict, string_types)):
        raise TypeError('info should be a dict or string')

    arg_list = [info['filename'], mri, bem, meg, eeg, n_jobs, verbose]
    cmd = 'dipole_fit(%s)' % (', '.join([str(a) for a in arg_list]))
    print cmd

    # set default forward solution coordinate frame to HEAD
    # this could, in principle, be an option
    coord_frame = FIFF.FIFFV_COORD_HEAD

    # Report the setup
    logger.info('MRI -> head transform source : %s' % mri)
    logger.info('Measurement data             : %s' % info['filename'])
    logger.info('BEM model                    : %s' % bem)
    logger.info('Do computations in %s coordinates',
                _coord_frame_name(coord_frame))

    return None

evoked = mne.read_evokeds(ave_fname, condition=0, baseline=(None, 0))
dip = dipole_fit(evoked, mri, bem, tmin=0.040, tmax=0.095, meg=True, eeg=False)
