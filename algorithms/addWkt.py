# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GeoRural
                                 A QGIS plugin
 Georreferenciamento de Imóveis Rurais
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-02-13
        copyright            : (C) 2022 by Tiago Prudencio e Leandro França
        email                : contato@geoone.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Tiago Prudencio e Leandro França'
__date__ = '2022-02-13'
__copyright__ = '(C) 2022 by Tiago Prudencio e Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsVectorLayer,
                       QgsGeometry,
                       QgsPoint,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.PyQt.QtGui import QIcon
from GeoINCRA.images.Imgs import *
import os


class addWkt(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):

        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return addWkt()

    def name(self):

        return 'addWkt'

    def displayName(self):

        return self.tr('CSV do INCRA para camada PointZ')

    def group(self):

        return self.tr(self.groupId())

    def groupId(self):

        return ''

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/geoincra_pb.png'))

    def shortHelpString(self):
        txt = 'Esta ferramenta transforma um arquivo CSV de vértices do INCRA em uma camada do tipo PointZ.'

        footer = '''<div>
                      <div align="center">
                      <img style="width: 100%; height: auto;" src="data:image/jpg;base64,'''+ INCRA_GeoOne +'''
                      </div>
                      <div align="right">
                      <p align="right">
                      <a href="https://geoone.com.br/"><span style="font-weight: bold;">Clique aqui para conhecer o modelo GeoRural da GeoOne</span></a><br>
                      </p>
                      <a target="_blank" rel="noopener noreferrer" href="https://geoone.com.br/"><img title="GeoOne" src="data:image/png;base64,'''+ GeoOne +'''"></a>
                      <p><i>"Mapeamento automatizado, fácil e direto ao ponto é na GeoOne"</i></p>
                      </div>
                    </div>'''
        return txt + footer

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
        QgsProcessingParameterFile(
            self.INPUT,
            self.tr('Arquivo de entrada (*.csv)'),
            fileFilter= 'Arquivo de Valores Separados por Vírgulas (*.csv)'
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('vertices_Incra')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        my_wkt = self.parameterAsString(
            parameters,
            self.INPUT,
            context
        )

        if my_wkt is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        uri = "file:{}?delimiter={}&crs=epsg:4674&wktField={}".format(my_wkt,";", "GEOMETRIA_WKT")
        source = QgsVectorLayer(uri, "vertice", "delimitedtext")

        if not source.isValid():
            feedback.pushInfo("Layer failed to load!")
        else:
            feedback.pushInfo("Layer to load!")


        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            feature.setAttributes(feature.attributes())
            X = feature.geometry().asPoint().x()
            Y = feature.geometry().asPoint().y()
            Z = feature['Z']
            geom = QgsGeometry(QgsPoint(float(X), float(Y), float(Z)))
            feature.setGeometry(geom)
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
