#  IRIS Source Code
#  Copyright (C) 2024 - DFIR-IRIS
#  contact@dfir-iris.org
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphene import List
from graphene.relay import Node
from graphene.relay import Connection
from graphene import Field
from graphene import Mutation
from graphene import NonNull
from graphene import Int
from graphene import Float
from graphene import String

from app.models.cases import Cases
from app.blueprints.graphql.iocs import IOCObject
from app.business.iocs import get_iocs
from app.business.cases import create
from app.business.cases import delete
from app.business.cases import update

from app.blueprints.graphql.iocs import IOCConnection


class CaseObject(SQLAlchemyObjectType):
    class Meta:
        model = Cases
        interfaces = [Node]

    # TODO add filters
    # TODO do pagination (maybe present it as a relay Connection?)
    iocs = SQLAlchemyConnectionField(IOCConnection, iocId=Float(), iocUuid=String(), iocValue=String(), iocTypeId=Int(), iocDescription=String(), iocTags=String(), iocMisp=String())

    @staticmethod
    def resolve_iocs(root, info, **kwargs):
        query = IOCObject.get_query(info)
        if kwargs.get('iocId'):
            query = query.filter_by(ioc_id=kwargs['iocId'])
        if kwargs.get('iocUuid'):
            query = query.filter_by(ioc_uuid=kwargs['iocUuid'])
        if kwargs.get('iocValue'):
            query = query.filter_by(ioc_value=kwargs['iocValue'])
        if kwargs.get('iocTypeId'):
            query = query.filter_by(ioc_type_id=kwargs['iocTypeId'])
        if kwargs.get('iocDescription'):
            query = query.filter_by(ioc_description=kwargs['iocDescription'])
        if kwargs.get('iocTags'):
            query = query.filter_by(ioc_tags=kwargs['iocTags'])
        if kwargs.get('iocMisp'):
            query = query.filter_by(ioc_misp=kwargs['iocMisp'])
        return query


class CaseConnection(Connection):
    class Meta:
        node = CaseObject

    total_count = Int()

    @staticmethod
    def resolve_total_count(root, info, **kwargs):
        return root.length


class CaseCreate(Mutation):

    class Arguments:
        name = NonNull(String)
        description = NonNull(String)
        client_id = NonNull(Int)

        soc_id = String()
        classification_id = Int()

    case = Field(CaseObject)

    @staticmethod
    def mutate(root, info, name, description, client_id, soc_id=None, classification_id=None):
        request = {
            'case_name': name,
            'case_description': description,
            'case_customer': client_id,
            'case_soc_id': ''
        }
        if soc_id:
            request['case_soc_id'] = soc_id
        if classification_id:
            request['classification_id'] = classification_id
        case, _ = create(request)
        return CaseCreate(case=case)


class CaseDelete(Mutation):

    class Arguments:
        case_id = NonNull(Float)

    case = Field(CaseObject)

    @staticmethod
    def mutate(root, info, case_id):
        delete(case_id)


class CaseUpdate(Mutation):

    class Arguments:
        case_id = NonNull(Float)

        name = String()
        description = String()
        soc_id = String()
        classification_id = Int()
        severity_id = Int()
        client_id = Int()
        owner_id = Int()
        state_id = Int()
        review_status_id = Int()
        reviewer_id = Int()
        tags = String()

    case = Field(CaseObject)

    @staticmethod
    def mutate(root, info, case_id, name=None, soc_id=None, classification_id=None, client_id=None, description=None,
               severity_id=None, owner_id=None, state_id=None, reviewer_id=None, tags=None, review_status_id=None):
        request = {}
        if name:
            request['case_name'] = name
        if soc_id:
            request['case_soc_id'] = soc_id
        if classification_id:
            request['classification_id'] = classification_id
        if client_id:
            request['case_customer'] = client_id
        if description:
            request['case_description'] = description
        if severity_id:
            request['severity_id'] = severity_id
        if owner_id:
            request['owner_id'] = owner_id
        if state_id:
            request['state_id'] = state_id
        if reviewer_id:
            request['reviewer_id'] = reviewer_id
        if tags:
            request['case_tags'] = tags
        if review_status_id:
            request['review_status_id'] = review_status_id
        case, _ = update(case_id, request)
        return CaseUpdate(case=case)
