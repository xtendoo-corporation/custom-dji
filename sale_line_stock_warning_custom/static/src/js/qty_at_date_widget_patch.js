import { patch } from "@web/core/utils/patch";
import { QtyAtDateWidget } from "@sale_stock/widgets/qty_at_date_widget";

patch(QtyAtDateWidget.prototype, {
    get colorClass() {
        const { data } = this.props.record;
        if (
            data.free_qty_today < data.qty_to_deliver
            && data.virtual_available_at_date < data.qty_to_deliver
            && !data.is_mto
        ) {
            return "text-danger";
        }
        if (data.free_qty_today >= data.qty_to_deliver) {
            return "text-primary";
        }
        return "text-warning";
    },
});
