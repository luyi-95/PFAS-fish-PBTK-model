"""Run archived offline design code with only input/output roots rebound, outside package."""
import ast,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
assert len(sys.argv)==2,'usage: python -B tools/reproduce_heldout_design.py NEW_EXTERNAL_OUTPUT_DIR'
dest=Path(sys.argv[1]).resolve()
assert not dest.is_relative_to(root) and not dest.exists(),'New external output only'
source=root/'tools/heldout_preflight_frozen.py'
class RebindRoots(ast.NodeTransformer):
    def visit_Assign(self,node):
        if len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            if node.targets[0].id=='V1':node.value=ast.Name(id='input_root',ctx=ast.Load())
            elif node.targets[0].id=='OUT':node.value=ast.Name(id='output_root',ctx=ast.Load())
        return node
tree=RebindRoots().visit(ast.parse(source.read_text()));ast.fix_missing_locations(tree)
exec(compile(tree,str(source),'exec'),{'__file__':str(source),'input_root':root/'reference_v1','output_root':dest})
