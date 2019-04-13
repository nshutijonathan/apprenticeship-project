import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.register.models import Register


class RegisterType(DjangoObjectType):
    class Meta:
        model = Register


class Query(graphene.ObjectType):
    """
    Return a list of registers.
    Or return a single register specified.
    """

    registers = graphene.List(RegisterType)
    register = graphene.Field(RegisterType, id=graphene.Int())

    @login_required
    def resolve_registers(self, info, **kwargs):
        return Register.objects.all()

    @login_required
    def resolve_register(self, info, **kwargs):
        id = kwargs.get('id')
        get_one_register = Register.objects.get(pk=id)
        if(get_one_register):
            return get_one_register
        else:
            raise ObjectDoesNotExist(f'Register with id {id} was not found')

        return None
