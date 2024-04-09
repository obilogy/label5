# label5
Simple and fast annotator for machine learning tasks.

<p align="center">
  <img src="https://github.com/obilogy/label5/blob/main/label5demo_wikipedia_img.png" width="50%" height="50%">
</p>

For me, it has been great for pipeline optimization.

To add your own labels, find:

    def setup_label_list(self):
        labels = ["particle", ...]
        self.labelList.addItems(labels)
        self.labelList.itemClicked.connect(self.on_label_item_clicked)

and add your own labels.

label5 supports bounding box annotations (left click and drag), and polyline annotations (right click and drag). You can toggle on/off the autocompletion of polylines in the GUI.

Annotations are also saved in normalized format in case you need it. Lastly, the polyline annotations are in "points" format, and not in RLE format. 

I will update it according to my labeling needs. Suggestions, comments, questions and contributions are welcome.
