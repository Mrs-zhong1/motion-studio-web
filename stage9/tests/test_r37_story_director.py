"""R37 continuous-story acceptance migrated to R39 final five-act engine.

Legacy .r37-stage DOM was removed in favor of the APPROVED ZIP's one
continuous camera/story timeline. Keep this compatibility entrypoint but
assert R39's actual five visible acts using its maintained browser test.
"""
from test_r39_cinematic_browser import run

if __name__=='__main__':
 run()
 print('R37→R39 PASS: actual five distinct film chapters and continuous scroll director')
