/***************************************************************************
    qgsrulebasedlabeling.cpp
    ---------------------
    begin                : September 2015
    copyright            : (C) 2015 by Martin Dobias
    email                : wonder dot sk at gmail dot com
 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
#include "qgsrulebasedlabeling.h"


QgsRuleBasedLabelProvider::QgsRuleBasedLabelProvider( const QgsRuleBasedLabeling& rules, QgsVectorLayer* layer, bool withFeatureLoop )
    : QgsVectorLayerLabelProvider( layer, withFeatureLoop )
    , mRules( rules )
{
  mRules.rootRule()->createSubProviders( layer, mSubProviders, this );
}

QgsRuleBasedLabelProvider::~QgsRuleBasedLabelProvider()
{
  // sub-providers owned by labeling engine
}

QgsVectorLayerLabelProvider *QgsRuleBasedLabelProvider::createProvider( QgsVectorLayer *layer, bool withFeatureLoop, const QgsPalLayerSettings *settings )
{
  return new QgsVectorLayerLabelProvider( layer, withFeatureLoop, settings );
}

bool QgsRuleBasedLabelProvider::prepare( const QgsRenderContext& context, QStringList& attributeNames )
{
  Q_FOREACH ( QgsVectorLayerLabelProvider* provider, mSubProviders )
    provider->setEngine( mEngine );

  // populate sub-providers
  mRules.rootRule()->prepare( context, attributeNames, mSubProviders );
  return true;
}

void QgsRuleBasedLabelProvider::registerFeature( QgsFeature& feature, QgsRenderContext &context, QgsGeometry* obstacleGeometry )
{
  // will register the feature to relevant sub-providers
  mRules.rootRule()->registerFeature( feature, context, mSubProviders, obstacleGeometry );
}

QList<QgsAbstractLabelProvider*> QgsRuleBasedLabelProvider::subProviders()
{
  QList<QgsAbstractLabelProvider*> lst;
  Q_FOREACH ( QgsVectorLayerLabelProvider* subprovider, mSubProviders )
    lst << subprovider;
  return lst;
}


////////////////////

QgsRuleBasedLabeling::Rule::Rule( QgsPalLayerSettings* settings, int scaleMinDenom, int scaleMaxDenom, const QString& filterExp, const QString& description, bool elseRule )
    : mParent( nullptr ), mSettings( settings )
    , mScaleMinDenom( scaleMinDenom ), mScaleMaxDenom( scaleMaxDenom )
    , mFilterExp( filterExp ), mDescription( description )
    , mElseRule( elseRule )
    , mIsActive( true )
    , mFilter( nullptr )
{
  initFilter();
}

QgsRuleBasedLabeling::Rule::~Rule()
{
  delete mSettings;
  delete mFilter;
  qDeleteAll( mChildren );
  // do NOT delete parent
}

void QgsRuleBasedLabeling::Rule::setSettings( QgsPalLayerSettings* settings )
{
  if ( mSettings == settings )
    return;

  delete mSettings;
  mSettings = settings;
}

void QgsRuleBasedLabeling::Rule::initFilter()
{
  if ( mElseRule || mFilterExp.compare( "ELSE", Qt::CaseInsensitive ) == 0 )
  {
    mElseRule = true;
    mFilter = nullptr;
  }
  else if ( !mFilterExp.isEmpty() )
  {
    delete mFilter;
    mFilter = new QgsExpression( mFilterExp );
  }
  else
  {
    mFilter = nullptr;
  }
}

void QgsRuleBasedLabeling::Rule::updateElseRules()
{
  mElseRules.clear();
  Q_FOREACH ( Rule* rule, mChildren )
  {
    if ( rule->isElse() )
      mElseRules << rule;
  }
}


void QgsRuleBasedLabeling::Rule::appendChild( QgsRuleBasedLabeling::Rule* rule )
{
  mChildren.append( rule );
  rule->mParent = this;
  updateElseRules();
}

void QgsRuleBasedLabeling::Rule::insertChild( int i, QgsRuleBasedLabeling::Rule* rule )
{
  mChildren.insert( i, rule );
  rule->mParent = this;
  updateElseRules();
}

void QgsRuleBasedLabeling::Rule::removeChildAt( int i )
{
  delete mChildren.at( i );
  mChildren.removeAt( i );
  updateElseRules();
}

QgsRuleBasedLabeling::Rule*QgsRuleBasedLabeling::Rule::clone() const
{
  QgsPalLayerSettings* s = mSettings ? new QgsPalLayerSettings( *mSettings ) : nullptr;
  Rule* newrule = new Rule( s, mScaleMinDenom, mScaleMaxDenom, mFilterExp, mDescription );
  newrule->setActive( mIsActive );
  // clone children
  Q_FOREACH ( Rule* rule, mChildren )
    newrule->appendChild( rule->clone() );
  return newrule;
}

QgsRuleBasedLabeling::Rule*QgsRuleBasedLabeling::Rule::create( const QDomElement& ruleElem )
{
  QgsPalLayerSettings* settings = nullptr;
  QDomElement settingsElem = ruleElem.firstChildElement( "settings" );
  if ( !settingsElem.isNull() )
  {
    settings = new QgsPalLayerSettings;
    settings->readXml( settingsElem );
  }

  QString filterExp = ruleElem.attribute( "filter" );
  QString description = ruleElem.attribute( "description" );
  int scaleMinDenom = ruleElem.attribute( "scalemindenom", "0" ).toInt();
  int scaleMaxDenom = ruleElem.attribute( "scalemaxdenom", "0" ).toInt();
  //QString ruleKey = ruleElem.attribute( "key" );
  Rule* rule = new Rule( settings, scaleMinDenom, scaleMaxDenom, filterExp, description );

  //if ( !ruleKey.isEmpty() )
  //  rule->mRuleKey = ruleKey;

  rule->setActive( ruleElem.attribute( "active", "1" ).toInt() );

  QDomElement childRuleElem = ruleElem.firstChildElement( "rule" );
  while ( !childRuleElem.isNull() )
  {
    Rule* childRule = create( childRuleElem );
    if ( childRule )
    {
      rule->appendChild( childRule );
    }
    else
    {
      //QgsDebugMsg( "failed to init a child rule!" );
    }
    childRuleElem = childRuleElem.nextSiblingElement( "rule" );
  }

  return rule;
}

QDomElement QgsRuleBasedLabeling::Rule::save( QDomDocument& doc ) const
{
  QDomElement ruleElem = doc.createElement( "rule" );

  if ( mSettings )
  {
    ruleElem.appendChild( mSettings->writeXml( doc ) );
  }
  if ( !mFilterExp.isEmpty() )
    ruleElem.setAttribute( "filter", mFilterExp );
  if ( mScaleMinDenom != 0 )
    ruleElem.setAttribute( "scalemindenom", mScaleMinDenom );
  if ( mScaleMaxDenom != 0 )
    ruleElem.setAttribute( "scalemaxdenom", mScaleMaxDenom );
  if ( !mDescription.isEmpty() )
    ruleElem.setAttribute( "description", mDescription );
  if ( !mIsActive )
    ruleElem.setAttribute( "active", 0 );
  //ruleElem.setAttribute( "key", mRuleKey );

  for ( RuleList::const_iterator it = mChildren.constBegin(); it != mChildren.constEnd(); ++it )
  {
    Rule* rule = *it;
    ruleElem.appendChild( rule->save( doc ) );
  }
  return ruleElem;
}

void QgsRuleBasedLabeling::Rule::createSubProviders( QgsVectorLayer* layer, QgsRuleBasedLabeling::RuleToProviderMap& subProviders, QgsRuleBasedLabelProvider *provider )
{
  if ( mSettings )
  {
    // add provider!
    QgsVectorLayerLabelProvider *p = provider->createProvider( layer, false, mSettings );
    delete subProviders.value( this, nullptr );
    subProviders[this] = p;
  }

  // call recursively
  Q_FOREACH ( Rule* rule, mChildren )
  {
    rule->createSubProviders( layer, subProviders, provider );
  }
}

void QgsRuleBasedLabeling::Rule::prepare( const QgsRenderContext& context, QStringList& attributeNames, QgsRuleBasedLabeling::RuleToProviderMap& subProviders )
{
  if ( mSettings )
  {
    QgsVectorLayerLabelProvider* p = subProviders[this];
    if ( !p->prepare( context, attributeNames ) )
    {
      subProviders.remove( this );
      delete p;
    }
  }

  if ( mFilter )
  {
    attributeNames << mFilter->referencedColumns();
    mFilter->prepare( &context.expressionContext() );
  }

  // call recursively
  Q_FOREACH ( Rule* rule, mChildren )
  {
    rule->prepare( context, attributeNames, subProviders );
  }
}

QgsRuleBasedLabeling::Rule::RegisterResult QgsRuleBasedLabeling::Rule::registerFeature( QgsFeature& feature, QgsRenderContext &context, QgsRuleBasedLabeling::RuleToProviderMap& subProviders, QgsGeometry* obstacleGeometry )
{
  if ( !isFilterOK( feature, context )
       || !isScaleOK( context.rendererScale() ) )
    return Filtered;

  bool registered = false;

  Q_ASSERT( !mSettings == subProviders.contains( this ) );

  // do we have active subprovider for the rule?
  if ( subProviders.contains( this ) && mIsActive )
  {
    subProviders[this]->registerFeature( feature, context, obstacleGeometry );
    registered = true;
  }

  bool willRegisterSomething = false;

  // call recursively
  Q_FOREACH ( Rule* rule, mChildren )
  {
    // Don't process else rules yet
    if ( !rule->isElse() )
    {
      RegisterResult res = rule->registerFeature( feature, context, subProviders, obstacleGeometry );
      // consider inactive items as "registered" so the else rule will ignore them
      willRegisterSomething |= ( res == Registered || res == Inactive );
      registered |= willRegisterSomething;
    }
  }

  // If none of the rules passed then we jump into the else rules and process them.
  if ( !willRegisterSomething )
  {
    Q_FOREACH ( Rule* rule, mElseRules )
    {
      registered |= rule->registerFeature( feature, context, subProviders, obstacleGeometry ) != Filtered;
    }
  }

  if ( !mIsActive )
    return Inactive;
  else if ( registered )
    return Registered;
  else
    return Filtered;
}

bool QgsRuleBasedLabeling::Rule::isFilterOK( QgsFeature& f, QgsRenderContext& context ) const
{
  if ( ! mFilter || mElseRule )
    return true;

  context.expressionContext().setFeature( f );
  QVariant res = mFilter->evaluate( &context.expressionContext() );
  return res.toInt() != 0;
}

bool QgsRuleBasedLabeling::Rule::isScaleOK( double scale ) const
{
  if ( qgsDoubleNear( scale, 0.0 ) ) // so that we can count features in classes without scale context
    return true;
  if ( mScaleMinDenom == 0 && mScaleMaxDenom == 0 )
    return true;
  if ( mScaleMinDenom != 0 && mScaleMinDenom > scale )
    return false;
  if ( mScaleMaxDenom != 0 && mScaleMaxDenom < scale )
    return false;
  return true;
}

////////////////////

QgsRuleBasedLabeling::QgsRuleBasedLabeling( QgsRuleBasedLabeling::Rule* root )
    : mRootRule( root )
{

}

QgsRuleBasedLabeling::QgsRuleBasedLabeling( const QgsRuleBasedLabeling& other )
{
  mRootRule = other.mRootRule->clone();
}

QgsRuleBasedLabeling::~QgsRuleBasedLabeling()
{
  delete mRootRule;
}

QgsRuleBasedLabeling*QgsRuleBasedLabeling::create( const QDomElement& element )
{
  QDomElement rulesElem = element.firstChildElement( "rules" );

  Rule* root = Rule::create( rulesElem );
  if ( !root )
    return nullptr;

  QgsRuleBasedLabeling* rl = new QgsRuleBasedLabeling( root );
  return rl;
}

QString QgsRuleBasedLabeling::type() const
{
  return "rule-based";
}

QDomElement QgsRuleBasedLabeling::save( QDomDocument& doc ) const
{
  QDomElement elem = doc.createElement( "labeling" );
  elem.setAttribute( "type", "rule-based" );

  QDomElement rulesElem = mRootRule->save( doc );
  rulesElem.setTagName( "rules" ); // instead of just "rule"
  elem.appendChild( rulesElem );

  return elem;
}

QgsVectorLayerLabelProvider* QgsRuleBasedLabeling::provider( QgsVectorLayer* layer ) const
{
  return new QgsRuleBasedLabelProvider( *this, layer, false );
}
