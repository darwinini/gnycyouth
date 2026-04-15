/**
 * Thank You Page Customization
 * Custom WooCommerce order received layout
 */

/**
 * Remove default WooCommerce thank you components
 */
add_action( 'init', function() {
    remove_action( 'woocommerce_thankyou', 'woocommerce_order_details_table', 10 );
});

/**
 * Hide default WooCommerce elements
 */
add_action( 'wp_head', function() {
    if ( ! is_wc_endpoint_url( 'order-received' ) ) return;

    echo '<style>
        .woocommerce-order-overview,
        .woocommerce-thankyou-order-received {
            display: none !important;
        }
    </style>';
});

/**
 * Remove default thank you text
 */
add_filter( 'woocommerce_thankyou_order_received_text', '__return_empty_string', 20 );

/**
 * Render custom thank you layout
 */
add_action( 'woocommerce_thankyou', 'custom_thankyou_layout', 10, 1 );
function custom_thankyou_layout( $order_id ) {

    $order = wc_get_order( $order_id );
    if ( ! $order ) return;

    // Order meta
    $pickup        = $order->get_meta( '_pickup_selections' );
    $church_name   = $order->get_meta( '_church_affiliation_name' );
    $has_alt       = $order->get_meta( '_has_alternate_pickup' );
    $alt_name      = $order->get_meta( '_alternate_pickup_name' );
    $alt_phone     = $order->get_meta( '_alternate_pickup_phone' );
    $alt_email     = $order->get_meta( '_alternate_pickup_email' );

    $is_pickup     = ! empty( $pickup ) && is_array( $pickup );

    $date_created  = $order->get_date_created();
?>

<style>
.thankyou-layout {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:24px;
    margin-top:30px;
}
@media (max-width:768px){
    .thankyou-layout{grid-template-columns:1fr;}
}
.thankyou-card{
    background:#fff;
    border:1px solid #e5e5e5;
    border-radius:8px;
    overflow:hidden;
}
.thankyou-card-header{
    background:#1a1a2e;
    color:#fff;
    padding:14px 20px;
    font-weight:bold;
}
.thankyou-card-body{padding:20px;}
.thankyou-row{
    display:flex;
    gap:12px;
    border-bottom:1px solid #f0f0f0;
    padding:10px 0;
}
.thankyou-row:last-child{border:none;}
.thankyou-label{font-weight:bold; min-width:120px;}
.thankyou-value{flex:1;}
.thankyou-order-table{
    width:100%;
    border-collapse:collapse;
}
.thankyou-order-table td,
.thankyou-order-table th{
    padding:10px 8px;
}
.thankyou-order-table th{
    text-align:left;
    border-bottom:2px solid #f0f0f0;
}
.thankyou-order-table td:last-child,
.thankyou-order-table th:last-child{
    text-align:right;
}
.thankyou-full-width{grid-column:1/-1;}
.thankyou-badge{
    background:#e8f0fe;
    padding:3px 10px;
    border-radius:20px;
    font-size:12px;
}
</style>

<div class="thankyou-layout">

    <!-- HEADER -->
    <div class="thankyou-card thankyou-full-width">
        <div class="thankyou-card-header" style="padding:20px;">
            <strong style="font-size:18px;">
                🎉 Thank you, <?php echo esc_html( $order->get_billing_first_name() ); ?>!
            </strong>

            <div style="margin-top:10px; display:flex; gap:30px; flex-wrap:wrap; font-size:13px;">

                <div>
                    <div>Order #</div>
                    <strong><?php echo esc_html( $order->get_order_number() ); ?></strong>
                </div>

                <div>
                    <div>Date</div>
                    <strong>
                        <?php
                        if ( $date_created ) {
                            echo esc_html( $date_created->date_i18n( 'F j, Y' ) );
                        }
                        ?>
                    </strong>
                </div>

                <div>
                    <div>Total</div>
                    <strong><?php echo wc_price( $order->get_total() ); ?></strong>
                </div>

                <div>
                    <div>Status</div>
                    <strong><?php echo esc_html( wc_get_order_status_name( $order->get_status() ) ); ?></strong>
                </div>

            </div>
        </div>
    </div>

    <!-- ORDER DETAILS -->
    <div class="thankyou-card">
        <div class="thankyou-card-header">🛍️ Order Details</div>
        <div class="thankyou-card-body">

            <table class="thankyou-order-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Qty</th>
                        <th>Total</th>
                    </tr>
                </thead>

                <tbody>
                <?php foreach ( $order->get_items() as $item ) :

                    $name  = $item->get_name();
                    $qty   = $item->get_quantity();
                    $total = wc_price( $item->get_total() );

                    $variations = [];

                    foreach ( $item->get_meta_data() as $meta ) {
                        if ( strpos( $meta->key, 'attribute_' ) !== false ) {

                            $key = str_replace(['attribute_pa_','attribute_'],'',$meta->key);
                            $key = ucwords(str_replace('-',' ',$key));

                            $val = is_scalar($meta->value) ? $meta->value : '';

                            $variations[] = $key . ': ' . ucfirst((string)$val);
                        }
                    }
                ?>
                    <tr>
                        <td>
                            <strong><?php echo esc_html($name); ?></strong>
                            <?php if ($variations): ?>
                                <div style="font-size:12px;color:#888;">
                                    <?php echo esc_html(implode(' · ',$variations)); ?>
                                </div>
                            <?php endif; ?>
                        </td>
                        <td>× <?php echo esc_html($qty); ?></td>
                        <td><?php echo $total; ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>

                <tfoot>

                    <?php if ( $order->get_subtotal() !== $order->get_total() ) : ?>
                    <tr>
                        <td colspan="2">Subtotal</td>
                        <td><?php echo wc_price( $order->get_subtotal() ); ?></td>
                    </tr>
                    <?php endif; ?>

                    <?php foreach ( $order->get_items('discount') as $discount ) : ?>
                    <tr>
                        <td colspan="2">Discount</td>
                        <td>-<?php echo wc_price( $discount->get_amount() ); ?></td>
                    </tr>
                    <?php endforeach; ?>

                    <tr>
                        <td colspan="2">Shipping</td>
                        <td>
                            <?php
                            foreach ( $order->get_shipping_methods() as $method ) {
                                echo '<span class="thankyou-badge">' . esc_html( $method->get_name() ) . '</span> ';
                            }
                            ?>
                        </td>
                    </tr>

                    <tr>
                        <td colspan="2"><strong>Total</strong></td>
                        <td><strong><?php echo wc_price( $order->get_total() ); ?></strong></td>
                    </tr>

                </tfoot>
            </table>

        </div>
    </div>

    <!-- RIGHT COLUMN -->
    <div style="display:flex; flex-direction:column; gap:24px;">

        <?php if ( $is_pickup ) : ?>
        <div class="thankyou-card">
            <div class="thankyou-card-header">📍 Pickup Details</div>
            <div class="thankyou-card-body">

                <div class="thankyou-row">
                    <span class="thankyou-label">Location</span>
                    <span class="thankyou-value">
                        <strong><?php echo esc_html( $pickup['location_name'] ?? '' ); ?></strong><br>
                        <small><?php echo esc_html( $pickup['location_address'] ?? '' ); ?></small>
                    </span>
                </div>

                <div class="thankyou-row">
                    <span class="thankyou-label">Date</span>
                    <span class="thankyou-value"><?php echo esc_html( $pickup['date_display'] ?? '' ); ?></span>
                </div>

                <div class="thankyou-row">
                    <span class="thankyou-label">Time</span>
                    <span class="thankyou-value"><?php echo esc_html( $pickup['time_display'] ?? '' ); ?></span>
                </div>

            </div>
        </div>
        <?php endif; ?>

        <?php if ( $church_name || $has_alt === 'yes' ) : ?>
        <div class="thankyou-card">
            <div class="thankyou-card-header">ℹ️ Additional Info</div>
            <div class="thankyou-card-body">

                <?php if ( $church_name ) : ?>
                <div class="thankyou-row">
                    <span class="thankyou-label">Church</span>
                    <span class="thankyou-value"><?php echo esc_html($church_name); ?></span>
                </div>
                <?php endif; ?>

                <?php if ( $has_alt === 'yes' ) : ?>
                <div class="thankyou-row">
                    <span class="thankyou-label">Alternate Pickup</span>
                    <span class="thankyou-value">
                        <?php echo esc_html($alt_name); ?><br>
                        <?php echo esc_html($alt_phone); ?><br>
                        <?php echo esc_html($alt_email); ?>
                    </span>
                </div>
                <?php endif; ?>

            </div>
        </div>
        <?php endif; ?>

        <!-- BILLING -->
        <div class="thankyou-card">
            <div class="thankyou-card-header">🏠 Billing</div>
            <div class="thankyou-card-body">
                <?php echo wp_kses_post( $order->get_formatted_billing_address() ); ?>
            </div>
        </div>

    </div>

</div>

<?php
}