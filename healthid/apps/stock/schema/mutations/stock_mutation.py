import graphene

from healthid.apps.stock.schema.mutations.open_stock_transfer \
    import OpenStockTransfer
from healthid.apps.stock.schema.mutations.close_stock_transfer \
    import CloseStockTransfer

from healthid.apps.stock.schema.mutations.create_stock_count_template \
    import CreateStockCountTemplate
from healthid.apps.stock.schema.mutations.delete_stock_count_template \
    import DeleteStockCountTemplate
from healthid.apps.stock.schema.mutations.edit_stock_count_template \
    import EditStockCountTemplate

from healthid.apps.stock.schema.mutations.initiate_stock_count \
    import InitiateStockCount
from healthid.apps.stock.schema.mutations.update_stock_count \
    import UpdateStockCount
from healthid.apps.stock.schema.mutations.delete_stock_count \
    import DeleteStockCount

from healthid.apps.stock.schema.mutations.remove_batch_stock \
    import RemoveBatchStock

from healthid.apps.stock.schema.mutations.reconcile_stock \
    import ReconcileStock


class Mutation(graphene.ObjectType):
    initiate_stock = InitiateStockCount.Field()
    update_stock = UpdateStockCount.Field()
    delete_stock = DeleteStockCount.Field()
    remove_batch_stock = RemoveBatchStock.Field()
    reconcile_stock = ReconcileStock.Field()
    open_stock_transfer = OpenStockTransfer.Field()
    close_stock_transfer = CloseStockTransfer.Field()
    create_stock_count_template = CreateStockCountTemplate.Field()
    edit_stock_count_template = EditStockCountTemplate.Field()
    delete_stock_count_template = DeleteStockCountTemplate.Field()
