from vision.vision import Vision
import cProfile

vis = Vision(False)
feats = vis.get_feat()
cProfile.run('vis.get_feat()')
