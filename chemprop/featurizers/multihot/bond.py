from typing import Iterable, Optional, Sequence

import numpy as np
from rdkit.Chem.rdchem import Bond

from chemprop.featurizers.multihot.base import MultiHotFeaturizer


class BondFeaturizer(MultiHotFeaturizer):
    def __init__(
        self, bond_types: Optional[Iterable[int]] = None, stereo: Optional[Sequence[int]] = None
    ):
        self.bond_types = set(bond_types or [1, 2, 3, 12])
        self.stereo = stereo or list(range(6))

        subfeature_sizes = [1, len(self.bond_types), 1, 1, (len(self.stereo) + 1)]
        self.__size = sum(subfeature_sizes)

        names = ("is_none", "bond_type", "conjugated", "ring", "stereo")
        offsets = np.cumsum([0] + subfeature_sizes[:-1])
        self.__subfeatures = dict(zip(names, offsets))
        
        super().__init__()

    def __len__(self):
        return self.__size

    @property
    def subfeatures(self) -> dict[str, int]:
        return self.__subfeatures

    def featurize(self, b: Bond) -> np.ndarray:
        x = np.zeros(len(self))

        if b is None:
            x[0] = 1
            return x

        bond_type = b.GetBondType()
        if bond_type is not None:
            i_bt = int(bond_type)
            CONJ_BIT = 5
            RING_BIT = 6

            if i_bt in self.bond_types:
                x[max(4, i_bt)] = 1
            if b.GetIsConjugated():
                x[CONJ_BIT] = 1
            if b.IsInRing():
                x[RING_BIT] = 1

        stereo_bit, _ = self.safe_index(int(b.GetStereo()), self.stereo)
        x[stereo_bit] = 1

        return x
