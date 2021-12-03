import pickle
import os


def dbInit(db):
    d= dict(
        data=dict(),
        ref=dict(),
        analysis=dict()
            )
    pickle.dump(d, open(os.path.join(db), 'wb'))
