# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


def chunks(listing, chunk_size):
    """
    Yield successive chunks from listing. Chunkify!
    """
    for i in range(0, len(listing), chunk_size):
        yield listing[i : i + chunk_size]
