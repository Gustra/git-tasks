here=$(readlink -f $(dirname ${BASH_SOURCE[0]}))

export PATH=${here}/bin:${PATH}
