<?xml version="1.0" encoding="UTF-8"?>
<!--
  テスト用の小さな CityGML（手書き・架空のデータ。実在の建物ではありません）
  - 建物A: LOD0 屋根形状あり、用途コードあり、階数が不明値(9999)、洪水想定が2件、延べ床面積あり
  - 建物B: LOD0 なし、LOD1 立体の底面からフットプリントを作る
  - 建物C: 形状なし → 変換結果から除外される
  座標は EPSG:6697（緯度 経度 標高）の順
-->
<core:CityModel
    xmlns:core="http://www.opengis.net/citygml/2.0"
    xmlns:bldg="http://www.opengis.net/citygml/building/2.0"
    xmlns:gml="http://www.opengis.net/gml"
    xmlns:gen="http://www.opengis.net/citygml/generics/2.0"
    xmlns:uro="https://www.geospatial.jp/iur/uro/3.2"
    xmlns:xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0">
  <core:cityObjectMember>
    <bldg:Building gml:id="bldg_test_a">
      <gml:name>テストビルA</gml:name>
      <gen:stringAttribute name="地区計画">
        <gen:value>テスト地区</gen:value>
      </gen:stringAttribute>
      <bldg:class codeSpace="../../codelists/Building_class.xml">3002</bldg:class>
      <bldg:usage codeSpace="../../codelists/Building_usage.xml">401</bldg:usage>
      <bldg:measuredHeight uom="m">31.5</bldg:measuredHeight>
      <bldg:storeysAboveGround>9999</bldg:storeysAboveGround>
      <bldg:storeysBelowGround>1</bldg:storeysBelowGround>
      <bldg:lod0RoofEdge>
        <gml:MultiSurface>
          <gml:surfaceMember>
            <gml:Polygon>
              <gml:exterior>
                <gml:LinearRing>
                  <gml:posList>35.6800 139.7600 0 35.6800 139.7610 0 35.6810 139.7610 0 35.6810 139.7600 0 35.6800 139.7600 0</gml:posList>
                </gml:LinearRing>
              </gml:exterior>
            </gml:Polygon>
          </gml:surfaceMember>
        </gml:MultiSurface>
      </bldg:lod0RoofEdge>
      <bldg:address>
        <core:Address>
          <core:xalAddress>
            <xAL:AddressDetails>
              <xAL:Country>
                <xAL:CountryName>日本</xAL:CountryName>
                <xAL:Locality>
                  <xAL:LocalityName Type="Town">東京都テスト区一丁目</xAL:LocalityName>
                </xAL:Locality>
              </xAL:Country>
            </xAL:AddressDetails>
          </core:xalAddress>
        </core:Address>
      </bldg:address>
      <uro:buildingDetailAttribute>
        <uro:BuildingDetailAttribute>
          <uro:totalFloorArea uom="m2">1234.5</uro:totalFloorArea>
        </uro:BuildingDetailAttribute>
      </uro:buildingDetailAttribute>
      <uro:buildingIDAttribute>
        <uro:BuildingIDAttribute>
          <uro:buildingID>13999-bldg-1</uro:buildingID>
        </uro:BuildingIDAttribute>
      </uro:buildingIDAttribute>
      <uro:bldgDisasterRiskAttribute>
        <uro:RiverFloodingRiskAttribute>
          <uro:description codeSpace="../../codelists/RiverFloodingRiskAttribute_description.xml">10</uro:description>
          <uro:depth uom="m">0.5</uro:depth>
          <uro:scale codeSpace="../../codelists/RiverFloodingRiskAttribute_scale.xml">2</uro:scale>
        </uro:RiverFloodingRiskAttribute>
      </uro:bldgDisasterRiskAttribute>
      <uro:bldgDisasterRiskAttribute>
        <uro:RiverFloodingRiskAttribute>
          <uro:description codeSpace="../../codelists/RiverFloodingRiskAttribute_description.xml">11</uro:description>
          <uro:depth uom="m">1.2</uro:depth>
          <uro:scale codeSpace="../../codelists/RiverFloodingRiskAttribute_scale.xml">1</uro:scale>
        </uro:RiverFloodingRiskAttribute>
      </uro:bldgDisasterRiskAttribute>
    </bldg:Building>
  </core:cityObjectMember>
  <core:cityObjectMember>
    <bldg:Building gml:id="bldg_test_b">
      <bldg:usage codeSpace="../../codelists/Building_usage.xml">411</bldg:usage>
      <bldg:measuredHeight uom="m">7</bldg:measuredHeight>
      <bldg:lod1Solid>
        <gml:Solid>
          <gml:exterior>
            <gml:CompositeSurface>
              <!-- 上面 z=10 -->
              <gml:surfaceMember>
                <gml:Polygon>
                  <gml:exterior><gml:LinearRing>
                    <gml:posList>35.6820 139.7620 10 35.6830 139.7620 10 35.6830 139.7630 10 35.6820 139.7630 10 35.6820 139.7620 10</gml:posList>
                  </gml:LinearRing></gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <!-- 側面（高さが変わるので底面候補にならない） -->
              <gml:surfaceMember>
                <gml:Polygon>
                  <gml:exterior><gml:LinearRing>
                    <gml:posList>35.6820 139.7620 3 35.6820 139.7630 3 35.6820 139.7630 10 35.6820 139.7620 10 35.6820 139.7620 3</gml:posList>
                  </gml:LinearRing></gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <!-- 底面 z=3 -->
              <gml:surfaceMember>
                <gml:Polygon>
                  <gml:exterior><gml:LinearRing>
                    <gml:posList>35.6820 139.7620 3 35.6820 139.7630 3 35.6830 139.7630 3 35.6830 139.7620 3 35.6820 139.7620 3</gml:posList>
                  </gml:LinearRing></gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
    </bldg:Building>
  </core:cityObjectMember>
  <core:cityObjectMember>
    <bldg:Building gml:id="bldg_test_c_no_geometry">
      <bldg:measuredHeight uom="m">5</bldg:measuredHeight>
    </bldg:Building>
  </core:cityObjectMember>
</core:CityModel>
