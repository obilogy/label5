# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
import sys
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os

class CustomPolylineItem(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.path = QPainterPath()
        self.label = None
        self.data_point_type = None
        #print("Path:", self.path)

    def add_point(self, point):
        if self.path.elementCount() == 0:
            self.path.moveTo(point)
        else:
            self.path.lineTo(point)
        self.setPath(self.path)

    def close_path(self):
        self.path.closeSubpath()
        self.setPath(self.path)

    def set_label(self, label: str):
        if not label.isspace() and label != "":
            label_item = QGraphicsTextItem(label, self)
            label_item.setPos(self.path.pointAtPercent(0))
            self.label = label

    def set_data_point_type(self, data_point_type: str):
        if not data_point_type.isspace() and data_point_type != "":
            self.data_point_type = data_point_type


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rect_item = None
        self.polyline_item = None
        self.viewport().setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            items = self.scene().items(scene_pos)
            
            # Deselect all items before drawing a new bounding box
            for item in self.scene().selectedItems():
                item.setSelected(False)

            # Draw a new bounding box if no QGraphicsRectItem is clicked
            if not any(isinstance(item, QGraphicsRectItem) for item in items):
                self.rect_item = QGraphicsRectItem(QRectF(scene_pos, QSizeF(0, 0)))
                self.rect_item.setBrush(QBrush(QColor(255, 0, 0, 100)))
                self.rect_item.setPen(QPen(Qt.blue, 2))
                self.rect_item.setFlag(QGraphicsItem.ItemIsSelectable)
                self.scene().addItem(self.rect_item)
            else:
                # Select the clicked QGraphicsRectItem
                for item in items:
                    if isinstance(item, QGraphicsRectItem):
                        item.setSelected(True)
                        break
        if event.button() == Qt.RightButton:
            scene_pos = self.mapToScene(event.pos())
            self.polyline_item = CustomPolylineItem()
            self.polyline_item.add_point(scene_pos)
            self.scene().addItem(self.polyline_item)


    def mouseMoveEvent(self, event):
        if self.rect_item:
            scene_pos = self.mapToScene(event.pos())
            rect = self.rect_item.rect()
            rect.setBottomRight(scene_pos)
            self.rect_item.setRect(rect)

        if self.polyline_item and event.buttons() == Qt.RightButton:
            scene_pos = self.mapToScene(event.pos())
            self.polyline_item.add_point(scene_pos)

    def mouseReleaseEvent(self, event):
        if self.rect_item:
            self.rect_item = None
        if self.polyline_item and event.button() == Qt.RightButton:
            if self.viewport().window().closePathEnabled:  # Access the flag via the parent window
                self.polyline_item.close_path()
            self.polyline_item = None

    def get_rect_item(self):
        items = self.scene().items()
        for item in items:
            if isinstance(item, QGraphicsRectItem):
                return item
        return None

    def get_polyline_item(self):
        items = self.scene().items()
        for item in items:
            if isinstance(item, CustomPolylineItem):
                return item
        return None

    def zoom_in(self, factor=1.25):
        """Zooms into the image by a given factor."""
        self.scale(factor, factor)

    def zoom_out(self, factor=1.25):
        """Zooms out of the image by a given factor."""
        self.scale(1 / factor, 1 / factor)

    def wheelEvent(self, event):
        """Overrides the default wheelEvent to implement zooming."""
        zoomInFactor = 1.25  # Define how much to zoom in
        zoomOutFactor = 1.25 / zoomInFactor  # Define how much to zoom out

        # Check the direction of the scroll (In or Out)
        if event.angleDelta().y() > 0:
            # Scroll up, zoom in
            self.zoom_in(zoomInFactor)
        else:
            # Scroll down, zoom out
            self.zoom_out(zoomOutFactor)

class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = CustomGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.controlArea = QWidget(self.centralwidget)
        self.controlArea.setMinimumSize(QSize(200, 0))
        self.controlArea.setObjectName("controlArea")
        self.verticalLayout = QVBoxLayout(self.controlArea)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadImagesButton = QPushButton(self.controlArea)
        self.loadImagesButton.setObjectName("loadImagesButton")
        self.verticalLayout.addWidget(self.loadImagesButton)
        self.previousImageButton = QPushButton(self.controlArea)
        self.previousImageButton.setObjectName("previousImageButton")
        self.verticalLayout.addWidget(self.previousImageButton)
        self.nextImageButton = QPushButton(self.controlArea)
        self.nextImageButton.setObjectName("nextImageButton")
        self.verticalLayout.addWidget(self.nextImageButton)
        self.labelList = QListWidget(self.controlArea)
        self.labelList.setObjectName("labelList")
        self.verticalLayout.addWidget(self.labelList)
        self.labelInput = QLineEdit(self.controlArea)
        self.labelInput.setObjectName("labelInput")
        self.verticalLayout.addWidget(self.labelInput)
        self.addLabelButton = QPushButton(self.controlArea)
        self.addLabelButton.setObjectName("addLabelButton")
        self.verticalLayout.addWidget(self.addLabelButton)
        self.dataPointTypeComboBox = QComboBox(self.controlArea)
        self.dataPointTypeComboBox.setObjectName("dataPointTypeComboBox")
        self.verticalLayout.addWidget(self.dataPointTypeComboBox)
        self.saveAnnotationsButton = QPushButton(self.controlArea)
        self.saveAnnotationsButton.setObjectName("saveAnnotationsButton")
        self.deleteSelectedButton = QPushButton(self.controlArea)
        self.deleteSelectedButton.setObjectName("deleteSelectedButton")
        self.verticalLayout.addWidget(self.deleteSelectedButton)
        self.verticalLayout.addWidget(self.saveAnnotationsButton)
        self.gridLayout.addWidget(self.controlArea, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toggleClosePathButton = QPushButton(self.controlArea)
        self.toggleClosePathButton.setObjectName("toggleClosePathButton")
        self.verticalLayout.addWidget(self.toggleClosePathButton)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Annotation Tool"))
        self.loadImagesButton.setText(_translate("MainWindow", "Load Images"))
        self.previousImageButton.setText(_translate("MainWindow", "Previous Image"))
        self.nextImageButton.setText(_translate("MainWindow", "Next Image"))
        self.addLabelButton.setText(_translate("MainWindow", "Add Label"))
        self.saveAnnotationsButton.setText(_translate("MainWindow", "Save Annotations"))
        self.deleteSelectedButton.setText(_translate("MainWindow", "Delete Selected"))
        self.toggleClosePathButton.setText(_translate("MainWindow", "Toggle Close Path"))



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.graphicsView.setScene(QGraphicsScene())
        self.rect_item = None
        self.labelInput.setPlaceholderText("Type new label or select from the list")
        self.loadImagesButton.clicked.connect(self.load_images)
        self.previousImageButton.clicked.connect(self.previous_image)
        self.nextImageButton.clicked.connect(self.next_image)
        self.addLabelButton.clicked.connect(self.add_label)
        self.saveAnnotationsButton.clicked.connect(self.save_annotations)
        self.deleteSelectedButton.clicked.connect(self.delete_selected)
        self.image_list = []
        self.current_image_index = -1
        self.setup_data_point_types()
        self.setup_label_list()
        self.image_width = None
        self.image_height = None
        self.toggleClosePathButton.clicked.connect(self.toggle_close_path)
        # Add an attribute to keep track of the path closing state
        self.closePathEnabled = True  # Paths will be closed by default

    # Add the toggle_close_path method to MainWindow
    def toggle_close_path(self):
        self.closePathEnabled = not self.closePathEnabled
        self.toggleClosePathButton.setText("Close Path: " + ("On" if self.closePathEnabled else "Off"))

    def delete_selected(self):
        selected_items = self.graphicsView.scene().selectedItems()
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem) or isinstance(item, CustomPolylineItem):
                child_items = item.childItems()
                for child in child_items:
                    self.graphicsView.scene().removeItem(child)
                self.graphicsView.scene().removeItem(item)

    def setup_data_point_types(self):
        shapes = ['empty square', 'empty circle', 'empty triangle up', 'empty triangle down', 'empty star', 'empty diamond', 'solid square', 'solid circle', 'solid triangle up', 'solid triangle down', 'solid star', 'solid diamond']
        colors = ['black', 'blue', 'red', 'green', 'gray', 'orange', 'magenta', 'yellow']

        for color in colors:
            for shape in shapes:
                self.dataPointTypeComboBox.addItem(f"{color} {shape}")

    def setup_label_list(self):
        #ADD YOUR LABELS HERE
        labels = ["particle", "x vs y complete plot", "data area", "X axis", "Y axis", "X axis major tick", "X axis minor tick", "Y axis major tick", "Y axis minor tick", "X axis label", "Y axis label", "Data point", "Plot Title", "X axis initial value", "X axis intermediate value", "X axis final value", "Y axis initial value", "Y axis intermediate value", "Y axis final value", "Error bar", "Trend line", "Complete legend", "Text from legend", "Data point from legend"]
        self.labelList.addItems(labels)
        self.labelList.itemClicked.connect(self.on_label_item_clicked)

    def on_label_item_clicked(self, item):
        self.labelInput.setText(item.text())

    def load_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Load Images", "", "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_paths:
            self.image_list.extend(file_paths)
            self.load_image(0)

    def load_image(self, index):
        if 0 <= index < len(self.image_list):
            self.graphicsView.scene().clear()
            image_path = self.image_list[index]
            pixmap = QPixmap(image_path)
            self.graphicsView.scene().addPixmap(pixmap)
            self.graphicsView.setSceneRect(QRectF(pixmap.rect()))
            self.current_image_index = index
            self.image_width = pixmap.width()
            self.image_height = pixmap.height()

    def previous_image(self):
        self.load_image(self.current_image_index - 1)

    def next_image(self):
        self.load_image(self.current_image_index + 1)

    def add_label(self):
        label = self.labelInput.text()
        rect_item = self.graphicsView.get_rect_item()
        polyline_item = self.graphicsView.get_polyline_item()
        data_point_type = self.dataPointTypeComboBox.currentText()

        if rect_item and not label.isspace() and label != "":
            label_item = QGraphicsTextItem(label, rect_item)
            label_item.setPos(rect_item.rect().topLeft())
            if label in ["Data point", "Data point from legend", "Error bar", "Text from legend"]:
                label_item.setPlainText(label + f" ({data_point_type})")
            self.labelInput.clear()

        elif polyline_item and not label.isspace() and label != "":
            label_item = QGraphicsTextItem(label, polyline_item)
            label_item.setPos(polyline_item.path.pointAtPercent(0))
            if label in ["particle", "Trend line"]:
                label_item.setPlainText(label + f" ({data_point_type})")
            polyline_item.label = label_item.toPlainText()
            self.labelInput.clear()

    def save_annotations(self):
        image_width = self.image_width
        image_height = self.image_height
        annotations = {}
        annotation_id = 0  # initialize annotation ID

        for idx, image_path in enumerate(self.image_list):
            image_annotations = []
            for item in self.graphicsView.scene().items():
                if isinstance(item, QGraphicsRectItem):
                    annotation_type = "bounding_box"

                    rect = item.rect()
                    label = None
                    data_point_type = None
                    for child in item.childItems():
                        if isinstance(child, QGraphicsTextItem):
                            label = child.toPlainText()
                            if "Data point" in label:
                                data_point_type = label[label.index("(")+1:label.index(")")]
                            break

                    if label is not None:
                        if data_point_type is not None:
                            color, shape = data_point_type.split(' ', 1)
                        else:
                            color, shape = None, None

                        annotation = {
                            'id': annotation_id,  # assign ID
                            'annotation_type': annotation_type,
                            'label': label,
                            'color': color,
                            'shape': shape,
                            'xmin': rect.left(),
                            'ymin': rect.top(),
                            'xmax': rect.right(),
                            'ymax': rect.bottom(),
                            'xmin_normalized': rect.left() / image_width,
                            'ymin_normalized': rect.top() / image_height,
                            'xmax_normalized': rect.right() / image_width,
                            'ymax_normalized': rect.bottom() / image_height
                        }
                        image_annotations.append(annotation)
                        annotation_id += 1  # increment ID

                elif isinstance(item, CustomPolylineItem):
                    annotation_type = "polyline"

                    label = item.label
                    data_point_type = item.data_point_type
                    points = []
                    normalized_points = []

                    for i in range(item.path.elementCount()):
                        element = item.path.elementAt(i)
                        points.append((element.x, element.y))
                        normalized_points.append((element.x / image_width, element.y / image_height))

                    if label is not None:
                        if data_point_type is not None:
                            color, shape = data_point_type.split(' ', 1)
                        else:
                            color, shape = None, None

                        annotation = {
                            'id': annotation_id,  # assign ID
                            'annotation_type': annotation_type,
                            'label': label,
                            'color': color,
                            'shape': shape,
                            'points': points,
                            'normalized_points': normalized_points
                        }
                        image_annotations.append(annotation)
                        annotation_id += 1  # increment ID

            annotations[image_path] = image_annotations

        for image_path, image_annotations in annotations.items():
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            annotation_filename = f"{image_name}_annotations.json"

            with open(annotation_filename, 'w') as f:
                json.dump(image_annotations, f)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
