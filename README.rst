======================================
Solar Documentation (work in progress)
======================================

Contents
========

- `0. Installation`_
- `1. Animation`_ 
    - `1.1 Change FPS`_
    - `1.2 Playblast`_
- `2. Attribute`_
    - `2.1 Channel Box Separator`_
    - `2.2 Transform Attributes`_
    - `2.3 Proxy Attribute`_
- `3. Cloth`_
    - `3.1 Cloth Setup`_
    - `3.2 Preroll`_
- `4. Curve`_
    - `4.1 Shapes`_ 
    - `4.2 Control`_
- `5. Display`_
    - `5.1 Color Node`_
- `6. Matrix`_
    - `6.1 Matrix Constraint`_
    - `6.2 Aim Matrix Constraint`_
- `7. Offset`_
    - `7.1 Offset Parent Matrix`_
- `8. Ribbon`_
    - `8.1 World Ribbon`_
    - `8.2 Bone Ribbon`_
- `9. Rig`_
    - `9.1 Cartoon Eye`_
    - `9.2 Spine`_
        - `9.2.1 Ik Spline Spine`_
        - `9.2.2 Ribbon Spine`_
        - `9.2.3 Matrix Ribbon Spine`_
- `10. Rivet`_
    - `10.1 Rivet Mesh`_ 
    - `10.2 Rivet Nurbs`_

0. Installation
===============

Go to **Code** and **Download ZIP**

Or if you have git, you can clone the repository:

.. code-block:: shell

    git clone https://github.com/DavidDelaunay43/Solar.git

Place the "Solar-main" folder into the maya script folder:

.. list-table:: 
   :header-rows: 1

   * - os
     - path
   * - linux
     - ~//maya/scripts
   * - mac os x
     - 	~/Library/Preferences/Autodesk/maya/scripts
   * - windows
     - /Users/<username>/Documents/maya/scripts

In Maya, create a Python tab in the script editor then run:

.. code-block:: python

    try:
        from Solar.ui import main_ui
    except ModuleNotFoundError:
        from Solar-main.ui import main_ui

1. Animation
============

1.1 Change FPS
--------------

1.2 Playblast
-------------

2. Attribute
============

2.1 Channel Box Separator
-------------------------

Creates or removes non-keable separator attribute on animation controllers.

.. image::
    .doc/channel_box_separator.gif

2.2 Transform Attributes
------------------------

Shortcut to Channel Control.

.. image::
    .doc/transform_attributes.gif

2.3 Proxy Attribute
-------------------

| In this example, we have a simple ik-fk setup with the switch attribute on a proxy node.
| To create a better setup for the animation, we create a proxy attribute on the controllers.

.. image::
    .doc/proxy_attribute.gif

3. Cloth
========

3.1 Cloth Setup
---------------

3.2 Preroll
-----------

3. Curve
========

4.1 Shapes
----------

Creates circle shapes under Transform or Joint nodes, with Normal along Primary Axis.

.. image::
    .doc/shapes.gif

4.2 Control
-----------

.. image::
    .doc/controls.gif

5. Display
==========

5.1 Color Node
--------------

.. image::
    .doc/color_node.gif

6. Matrix
=========

6.1 Matrix Constraint
---------------------

6.2 Aim Matrix Constraint
-------------------------

7. Offset
=========

7.1 Offset Parent Matrix
------------------------

In order to keep the World Matrix of a Transform or Joint node, we can use the offsetParentMatrix attribute.

.. image::
    .doc/offset_parent_matrix.gif

8. Ribbon
=========

8.1 World Ribbon
----------------

8.2 Bone Ribbon
---------------

9. Rig
======

9.2 Cartoon Eye
^^^^^^^^^^^^^^^

9.2 Spine
---------

9.2.1 Ik Spline Spine
^^^^^^^^^^^^^^^^^^^^^

9.2.2 Ribbon Spine
^^^^^^^^^^^^^^^^^^^

9.2.3 Matrix Ribbon Spine
^^^^^^^^^^^^^^^^^^^^^^^^^

10. Rivet
=========

10.1 Rivet Mesh
---------------

10.2 Rivet Nurbs
----------------
