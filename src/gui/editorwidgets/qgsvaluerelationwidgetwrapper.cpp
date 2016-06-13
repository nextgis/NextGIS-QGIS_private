/***************************************************************************
    qgsvaluerelationwidgetwrapper.cpp
     --------------------------------------
    Date                 : 5.1.2014
    Copyright            : (C) 2014 Matthias Kuhn
    Email                : matthias at opengis dot ch
 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include "qgsvaluerelationwidgetwrapper.h"

#include "qgis.h"
#include "qgsfield.h"
#include "qgsmaplayerregistry.h"
#include "qgsvaluerelationwidgetfactory.h"
#include "qgsvectorlayer.h"
#include "qgsfilterlineedit.h"

#include <QStringListModel>
#include <QCompleter>

bool QgsValueRelationWidgetWrapper::orderByKeyLessThan( const QgsValueRelationWidgetWrapper::ValueRelationItem& p1
    , const QgsValueRelationWidgetWrapper::ValueRelationItem& p2 )
{
  return qgsVariantLessThan( p1.first, p2.first );
}

bool QgsValueRelationWidgetWrapper::orderByValueLessThan( const QgsValueRelationWidgetWrapper::ValueRelationItem& p1
    , const QgsValueRelationWidgetWrapper::ValueRelationItem& p2 )
{
  return qgsVariantLessThan( p1.second, p2.second );
}

QgsValueRelationWidgetWrapper::QgsValueRelationWidgetWrapper( QgsVectorLayer* vl, int fieldIdx, QWidget* editor, QWidget* parent )
    : QgsEditorWidgetWrapper( vl, fieldIdx, editor, parent )
    , mComboBox( nullptr )
    , mListWidget( nullptr )
    , mLineEdit( nullptr )
    , mLayer( nullptr )
{
}


QVariant QgsValueRelationWidgetWrapper::value() const
{
  QVariant v;

  if ( mComboBox )
  {
    int cbxIdx = mComboBox->currentIndex();
    if ( cbxIdx > -1 )
    {
      v = mComboBox->itemData( mComboBox->currentIndex() );
    }
  }

  if ( mListWidget )
  {
    QStringList selection;
    for ( int i = 0; i < mListWidget->count(); ++i )
    {
      QListWidgetItem* item = mListWidget->item( i );
      if ( item->checkState() == Qt::Checked )
        selection << item->data( Qt::UserRole ).toString();
    }

    v = selection.join( "," ).prepend( '{' ).append( '}' );
  }

  if ( mLineEdit )
  {
    Q_FOREACH ( const ValueRelationItem& i , mCache )
    {
      if ( i.second == mLineEdit->text() )
      {
        v = i.first;
        break;
      }
    }
  }

  return v;
}

QWidget* QgsValueRelationWidgetWrapper::createWidget( QWidget* parent )
{
  if ( config( "AllowMulti" ).toBool() )
  {
    return new QListWidget( parent );
  }
  else if ( config( "UseCompleter" ).toBool() )
  {
    return new QgsFilterLineEdit( parent );
  }
  {
    return new QComboBox( parent );
  }
}

void QgsValueRelationWidgetWrapper::initWidget( QWidget* editor )
{
  mCache = createCache( config() );

  mComboBox = qobject_cast<QComboBox*>( editor );
  mListWidget = qobject_cast<QListWidget*>( editor );
  mLineEdit = qobject_cast<QLineEdit*>( editor );

  if ( mComboBox )
  {
    if ( config( "AllowNull" ).toBool() )
    {
      mComboBox->addItem( tr( "(no selection)" ), QVariant( field().type() ) );
    }

    Q_FOREACH ( const ValueRelationItem& element, mCache )
    {
      mComboBox->addItem( element.second, element.first );
    }

    connect( mComboBox, SIGNAL( currentIndexChanged( int ) ), this, SLOT( valueChanged() ) );
  }
  else if ( mListWidget )
  {
    Q_FOREACH ( const ValueRelationItem& element, mCache )
    {
      QListWidgetItem *item;
      item = new QListWidgetItem( element.second );
      item->setData( Qt::UserRole, element.first );

      mListWidget->addItem( item );
    }
    connect( mListWidget, SIGNAL( itemChanged( QListWidgetItem* ) ), this, SLOT( valueChanged() ) );
  }
  else if ( mLineEdit )
  {
    QStringList values;
    Q_FOREACH ( const ValueRelationItem& i,  mCache )
    {
      values << i.second;
    }

    QStringListModel* m = new QStringListModel( values, mLineEdit );
    QCompleter* completer = new QCompleter( m, mLineEdit );
    completer->setCaseSensitivity( Qt::CaseInsensitive );
    mLineEdit->setCompleter( completer );
  }
}

bool QgsValueRelationWidgetWrapper::valid() const
{
  return mListWidget || mLineEdit || mComboBox;
}

void QgsValueRelationWidgetWrapper::setValue( const QVariant& value )
{
  if ( mListWidget )
  {
    QStringList checkList = value.toString().remove( QChar( '{' ) ).remove( QChar( '}' ) ).split( ',' );

    for ( int i = 0; i < mListWidget->count(); ++i )
    {
      QListWidgetItem* item = mListWidget->item( i );
      if ( config( "OrderByValue" ).toBool() )
      {
        item->setCheckState( checkList.contains( item->data( Qt::UserRole ).toString() ) ? Qt::Checked : Qt::Unchecked );
      }
      else
      {
        item->setCheckState( checkList.contains( item->data( Qt::UserRole ).toString() ) ? Qt::Checked : Qt::Unchecked );
      }
    }
  }
  else if ( mComboBox )
  {
    mComboBox->setCurrentIndex( mComboBox->findData( value ) );
  }
  else if ( mLineEdit )
  {
    Q_FOREACH ( ValueRelationItem i, mCache )
    {
      if ( i.first == value )
      {
        mLineEdit->setText( i.second );
        break;
      }
    }
  }
}


QgsValueRelationWidgetWrapper::ValueRelationCache QgsValueRelationWidgetWrapper::createCache( const QgsEditorWidgetConfig& config )
{
  ValueRelationCache cache;

  QgsVectorLayer* layer = qobject_cast<QgsVectorLayer*>( QgsMapLayerRegistry::instance()->mapLayer( config.value( "Layer" ).toString() ) );

  if ( layer )
  {
    int ki = layer->fieldNameIndex( config.value( "Key" ).toString() );
    int vi = layer->fieldNameIndex( config.value( "Value" ).toString() );

    QgsExpressionContext context;
    context << QgsExpressionContextUtils::globalScope()
    << QgsExpressionContextUtils::projectScope()
    << QgsExpressionContextUtils::layerScope( layer );

    QgsExpression *e = nullptr;
    if ( !config.value( "FilterExpression" ).toString().isEmpty() )
    {
      e = new QgsExpression( config.value( "FilterExpression" ).toString() );
      if ( e->hasParserError() || !e->prepare( &context ) )
        ki = -1;
    }

    if ( ki >= 0 && vi >= 0 )
    {
      QSet<int> attributes;
      attributes << ki << vi;

      QgsFeatureRequest::Flags flags = QgsFeatureRequest::NoGeometry;

      bool requiresAllAttributes = false;
      if ( e )
      {
        if ( e->needsGeometry() )
          flags = QgsFeatureRequest::NoFlags;

        Q_FOREACH ( const QString& field, e->referencedColumns() )
        {
          if ( field == QgsFeatureRequest::AllAttributes )
          {
            requiresAllAttributes = true;
            break;
          }
          int idx = layer->fieldNameIndex( field );
          if ( idx < 0 )
            continue;
          attributes << idx;
        }
      }

      QgsFeatureRequest fr = QgsFeatureRequest().setFlags( flags );
      if ( !requiresAllAttributes )
      {
        fr.setSubsetOfAttributes( attributes.toList() );
      }

      QgsFeatureIterator fit = layer->getFeatures( fr );

      QgsFeature f;
      while ( fit.nextFeature( f ) )
      {
        context.setFeature( f );
        if ( e && !e->evaluate( &context ).toBool() )
          continue;

        cache.append( ValueRelationItem( f.attribute( ki ), f.attribute( vi ).toString() ) );
      }
    }
    delete e;
  }

  if ( config.value( "OrderByValue" ).toBool() )
  {
    qSort( cache.begin(), cache.end(), orderByValueLessThan );
  }
  else
  {
    qSort( cache.begin(), cache.end(), orderByKeyLessThan );
  }

  return cache;
}
