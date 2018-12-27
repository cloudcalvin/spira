import spira
from spira import param
from spira import shapes
from spira import LOG
from spira import RDD


# from spira.lpe.structure import ComposeMLayers
class PCell(spira.Cell):

    layer = param.LayerField(number=RDD.BAS.LAYER.number)
    width = param.FloatField(default=RDD.BAS.WIDTH)

    def create_elementals(self, elems):
        p0 = [[[0.3, 0.3], [3.6, 3]],
              [[1.45, 2.8], [2.45, 5]],
              [[1.25, 4.75], [2.65, 6]]]

        el = spira.ElementList()
        for points in p0:
            shape = shapes.RectangleShape(p1=points[0],
                                     p2=points[1],
                                     gdslayer=self.layer)
            el += shapes.Rectangle(shape=shape)

        # comp = ComposeMLayers(cell_elems=elems)
        cell = spira.Cell(elementals=el)
        elems += spira.SRef(cell)
        return elems


# ---------------------------------------------------------------------


if __name__ == '__main__':

    pcell = PCell()
    pcell.output()

