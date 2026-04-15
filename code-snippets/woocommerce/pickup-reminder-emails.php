/**
 * Pickup Reminder Emails
 * Sends day-before and morning-of reminders for scheduled pickups.
 */

/**
 * Schedule cron jobs on theme activation only.
 */
function schedule_pickup_reminder_crons() {
    if ( ! wp_next_scheduled( 'send_pickup_day_before_reminders' ) ) {
        $timezone = new DateTimeZone( wp_timezone_string() );
        $now      = new DateTime( 'now', $timezone );
        $next_8am = new DateTime( 'today 08:00:00', $timezone );

        if ( $now >= $next_8am ) {
            $next_8am->modify( '+1 day' );
        }

        wp_schedule_event(
            $next_8am->getTimestamp(),
            'daily',
            'send_pickup_day_before_reminders'
        );
    }

    if ( ! wp_next_scheduled( 'send_pickup_morning_reminders' ) ) {
        $timezone = new DateTimeZone( wp_timezone_string() );
        $now      = new DateTime( 'now', $timezone );
        $next_8am = new DateTime( 'today 08:00:00', $timezone );

        if ( $now >= $next_8am ) {
            $next_8am->modify( '+1 day' );
        }

        wp_schedule_event(
            $next_8am->getTimestamp(),
            'daily',
            'send_pickup_morning_reminders'
        );
    }
}
add_action( 'after_switch_theme', 'schedule_pickup_reminder_crons' );

/**
 * Clean up cron jobs when theme is switched away.
 */
function unschedule_pickup_reminder_crons() {
    wp_clear_scheduled_hook( 'send_pickup_day_before_reminders' );
    wp_clear_scheduled_hook( 'send_pickup_morning_reminders' );
}
add_action( 'switch_theme', 'unschedule_pickup_reminder_crons' );

// *** REMOVED the init safety net — it was causing duplicate cron registrations ***

/**
 * Get order details for reminder email.
 */
function get_pickup_email_order_details( $order_id ) {
    $order = wc_get_order( $order_id );
    if ( ! $order ) {
        return [];
    }

    $items = [];
    foreach ( $order->get_items() as $item ) {
        $product   = $item->get_product();
        $name      = $item->get_name();
        $qty       = $item->get_quantity();
        $subtotal  = wc_price( $item->get_subtotal() );
        $variation = [];

        if ( $product && $product->is_type( 'variation' ) ) {
            foreach ( $item->get_meta_data() as $meta ) {
                if ( strpos( $meta->key, 'attribute_' ) !== false ) {
                    $key         = str_replace( 'attribute_pa_', '', $meta->key );
                    $variation[] = ucfirst( $key ) . ': ' . ucfirst( $meta->value );
                }
            }
        }

        $items[] = [
            'name'      => $name,
            'qty'       => $qty,
            'subtotal'  => $subtotal,
            'variation' => implode( ', ', $variation ),
        ];
    }

    return [
        'order_number'  => $order->get_order_number(),
        'order_date'    => $order->get_date_created()->date_i18n( 'F j, Y' ),
        'order_total'   => wc_price( $order->get_total() ),
        'customer_name' => $order->get_billing_first_name() . ' ' . $order->get_billing_last_name(),
        'first_name'    => $order->get_billing_first_name(),
        'items'         => $items,
    ];
}

/**
 * Build reminder email HTML.
 */
function build_pickup_reminder_email( $booking, $order_details, $is_morning ) {
    $location_name    = get_the_title( $booking->location_id );
    $location_address = get_field( 'location_address', $booking->location_id );

    $date_obj     = DateTime::createFromFormat( 'Y-m-d', $booking->pickup_date );
    $date_display = $date_obj ? $date_obj->format( 'l, F j, Y' ) : $booking->pickup_date;

    $time_obj     = DateTime::createFromFormat( 'H:i', $booking->pickup_time );
    $time_display = $time_obj ? $time_obj->format( 'g:i A' ) : $booking->pickup_time;

    $subject = $is_morning
        ? '&#128205; Pickup Reminder: Your order is ready TODAY at ' . $time_display
        : '&#128197; Pickup Reminder: Your order pickup is TOMORROW — ' . $date_display;

    $heading_emoji = $is_morning ? '&#9888;&#65039;' : '&#128197;';
    $heading_text  = $is_morning ? 'Your Pickup is Today!' : 'Your Pickup is Tomorrow!';

    $greeting_line = $is_morning
        ? 'This is a friendly reminder that your order is ready for pickup <strong>today</strong>. Please review your pickup details below.'
        : 'This is a friendly reminder that your order is scheduled for pickup <strong>tomorrow</strong>. Please review your pickup details below.';

    $items_html = '';
    foreach ( $order_details['items'] as $item ) {
        $variation_html = ! empty( $item['variation'] )
            ? '<br><span style="font-size:12px;color:#888;">' . esc_html( $item['variation'] ) . '</span>'
            : '';

        $items_html .= '
        <tr>
            <td style="padding:10px 8px;border-bottom:1px solid #f0f0f0;vertical-align:top;">
                <span style="font-weight:bold;color:#1a1a2e;">' . esc_html( $item['name'] ) . '</span>
                ' . $variation_html . '
            </td>
            <td style="padding:10px 8px;border-bottom:1px solid #f0f0f0;text-align:center;vertical-align:top;">
                &times; ' . esc_html( $item['qty'] ) . '
            </td>
            <td style="padding:10px 8px;border-bottom:1px solid #f0f0f0;text-align:right;vertical-align:top;">
                ' . $item['subtotal'] . '
            </td>
        </tr>';
    }

    ob_start();
    ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title><?php echo esc_html( $heading_text ); ?></title>
    <style type="text/css">
        @media screen and (max-width: 620px) {
            .email-outer  { padding: 0 !important; }
            .email-inner  { width: 100% !important; max-width: 100% !important; }
            .email-header { padding: 20px 16px !important; border-radius: 0 !important; }
            .email-header h1 { font-size: 18px !important; }
            .email-meta td { padding: 6px 4px !important; }
            .email-meta .meta-value { font-size: 13px !important; }
            .email-body   { padding: 20px 16px !important; }
            .email-footer { padding: 16px !important; border-radius: 0 !important; }
            .section-header td { padding: 12px 14px !important; font-size: 14px !important; }
        }
    </style>
</head>
<body style="margin:0;padding:0;background-color:#f0f0f0;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" border="0" class="email-outer" style="background-color:#f0f0f0;padding:32px 0;">
    <tr>
        <td align="center" style="padding:0 12px;">
            <table width="640" cellpadding="0" cellspacing="0" border="0" class="email-inner" style="max-width:640px;width:100%;">

                <!-- Header -->
                <tr>
                    <td class="email-header" style="background:#1a1a2e;border-radius:8px 8px 0 0;padding:28px 36px;text-align:center;">
                        <img src="https://cdn.gnycyouth.org/wp-content/uploads/2026/03/11033656/logo.png"
                             alt="<?php echo esc_attr( get_bloginfo( 'name' ) ); ?>"
                             width="80" style="display:block;margin:0 auto 16px;height:auto;border:0;"/>
                        <h1 style="color:#fff;margin:0 0 8px;font-size:22px;font-weight:bold;line-height:1.3;">
                            <?php echo $heading_emoji; ?> <?php echo esc_html( $heading_text ); ?>
                        </h1>
                        <table class="email-meta" cellspacing="0" cellpadding="0" border="0" style="margin:20px auto 0;width:100%;">
                            <tr>
                                <td style="text-align:center;padding:8px;color:#fff;">
                                    <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7;margin-bottom:4px;">Order Number</div>
                                    <div class="meta-value" style="font-size:16px;font-weight:bold;">#<?php echo esc_html( $order_details['order_number'] ); ?></div>
                                </td>
                                <td style="text-align:center;padding:8px;color:#fff;">
                                    <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7;margin-bottom:4px;">Pickup Date</div>
                                    <div class="meta-value" style="font-size:16px;font-weight:bold;"><?php echo esc_html( $date_display ); ?></div>
                                </td>
                                <td style="text-align:center;padding:8px;color:#fff;">
                                    <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7;margin-bottom:4px;">Pickup Time</div>
                                    <div class="meta-value" style="font-size:16px;font-weight:bold;"><?php echo esc_html( $time_display ); ?></div>
                                </td>
                                <td style="text-align:center;padding:8px;color:#fff;">
                                    <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.5px;opacity:0.7;margin-bottom:4px;">Total</div>
                                    <div class="meta-value" style="font-size:16px;font-weight:bold;"><?php echo $order_details['order_total']; ?></div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Body -->
                <tr>
                    <td class="email-body" style="background:#ffffff;padding:32px 36px;border-left:1px solid #e5e5e5;border-right:1px solid #e5e5e5;">

                        <p style="margin:0 0 20px;font-size:15px;color:#333;line-height:1.6;">
                            Hi <strong><?php echo esc_html( $order_details['first_name'] ); ?></strong>,
                        </p>
                        <p style="margin:0 0 24px;font-size:15px;color:#333;line-height:1.6;">
                            <?php echo $greeting_line; ?>
                        </p>

                        <!-- Pickup Details -->
                        <table cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom:24px;">
                            <tr>
                                <td class="section-header" style="background:#1a1a2e;color:#fff;padding:14px 20px;border-radius:6px 6px 0 0;font-weight:bold;font-size:15px;">
                                    &#128205; Pickup Details
                                </td>
                            </tr>
                            <tr>
                                <td style="border:1px solid #e5e5e5;border-top:none;border-radius:0 0 6px 6px;padding:0;">
                                    <table cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="padding:12px 16px;border-bottom:1px solid #f0f0f0;font-weight:bold;color:#555;width:130px;font-size:14px;">Location</td>
                                            <td style="padding:12px 16px;border-bottom:1px solid #f0f0f0;color:#333;font-size:14px;">
                                                <strong><?php echo esc_html( $location_name ); ?></strong><br>
                                                <span style="color:#888;font-size:12px;"><?php echo esc_html( $location_address ); ?></span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding:12px 16px;border-bottom:1px solid #f0f0f0;font-weight:bold;color:#555;font-size:14px;">Date</td>
                                            <td style="padding:12px 16px;border-bottom:1px solid #f0f0f0;color:#333;font-size:14px;"><?php echo esc_html( $date_display ); ?></td>
                                        </tr>
                                        <tr>
                                            <td style="padding:12px 16px;font-weight:bold;color:#555;font-size:14px;">Time</td>
                                            <td style="padding:12px 16px;color:#333;font-size:14px;"><?php echo esc_html( $time_display ); ?></td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>

                        <!-- Order Summary -->
                        <table cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom:24px;">
                            <tr>
                                <td class="section-header" style="background:#1a1a2e;color:#fff;padding:14px 20px;border-radius:6px 6px 0 0;font-weight:bold;font-size:15px;">
                                    &#128717;&#65039; Order Summary
                                </td>
                            </tr>
                            <tr>
                                <td style="border:1px solid #e5e5e5;border-top:none;border-radius:0 0 6px 6px;padding:0;">
                                    <table cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <thead>
                                            <tr style="background:#f8f8f8;">
                                                <th style="padding:10px 8px;text-align:left;font-size:12px;color:#555;font-weight:bold;border-bottom:2px solid #f0f0f0;">Product</th>
                                                <th style="padding:10px 8px;text-align:center;font-size:12px;color:#555;font-weight:bold;border-bottom:2px solid #f0f0f0;">Qty</th>
                                                <th style="padding:10px 8px;text-align:right;font-size:12px;color:#555;font-weight:bold;border-bottom:2px solid #f0f0f0;">Total</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <?php echo $items_html; ?>
                                        </tbody>
                                        <tfoot>
                                            <tr>
                                                <td colspan="2" style="padding:10px 8px;font-weight:bold;font-size:15px;color:#1a1a2e;border-top:2px solid #1a1a2e;">Order Total</td>
                                                <td style="padding:10px 8px;font-weight:bold;font-size:15px;color:#1a1a2e;border-top:2px solid #1a1a2e;text-align:right;"><?php echo $order_details['order_total']; ?></td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </td>
                            </tr>
                        </table>

                        <p style="margin:0 0 8px;font-size:14px;color:#555;line-height:1.6;">
                            Please bring your order confirmation when picking up your items. If you have any questions, don't hesitate to reach out.
                        </p>
                        <p style="margin:0;font-size:14px;color:#555;line-height:1.6;">
                            We look forward to seeing you!
                        </p>

                    </td>
                </tr>

                <!-- Footer -->
                <tr>
                    <td class="email-footer" style="background:#f8f8f8;border:1px solid #e5e5e5;border-top:none;border-radius:0 0 8px 8px;padding:24px 36px;text-align:center;">
                        <p style="margin:0 0 8px;font-size:13px;color:#555;">
                            If you have any questions about your order, contact us at
                            <a href="mailto:store@gnycyouth.org" style="color:#1a1a2e;font-weight:bold;">store@gnycyouth.org</a>
                        </p>
                        <p style="margin:0;font-size:12px;color:#888;">
                            <?php echo esc_html( get_bloginfo( 'name' ) ); ?><br>
                            7 Shelter Rock Rd, Manhasset, NY 11030
                        </p>
                    </td>
                </tr>

            </table>
        </td>
    </tr>
</table>

</body>
</html>
    <?php
    $html = ob_get_clean();

    return [
        'subject' => $subject,
        'html'    => $html,
    ];
}

/**
 * Send pickup reminder emails.
 * Transient-based lock prevents concurrent cron runs from sending duplicates.
 */
function send_pickup_reminders( $is_morning = false ) {
    global $wpdb;

    // Transient lock — if another process is already running this, bail out.
    $lock_key = 'pickup_reminder_lock_' . ( $is_morning ? 'morning' : 'day_before' );
    if ( get_transient( $lock_key ) ) {
        return;
    }
    set_transient( $lock_key, 1, 5 * MINUTE_IN_SECONDS );

    $table    = $wpdb->prefix . 'pickup_bookings';
    $timezone = new DateTimeZone( wp_timezone_string() );

    if ( $is_morning ) {
        $target_date = ( new DateTime( 'now', $timezone ) )->format( 'Y-m-d' );
        $column      = 'reminder_morning';
    } else {
        $target_date = ( new DateTime( 'tomorrow', $timezone ) )->format( 'Y-m-d' );
        $column      = 'reminder_day_before';
    }

    $bookings = $wpdb->get_results( $wpdb->prepare(
        "SELECT * FROM {$table} WHERE pickup_date = %s AND {$column} = 0",
        $target_date
    ) );

    if ( ! empty( $bookings ) ) {
        foreach ( $bookings as $booking ) {

            // Atomic lock — only send if we're the one who flips the flag.
            $rows_affected = $wpdb->query( $wpdb->prepare(
                "UPDATE {$table} SET {$column} = 1 WHERE id = %d AND {$column} = 0",
                $booking->id
            ) );

            if ( ! $rows_affected ) {
                continue;
            }

            $order_details = get_pickup_email_order_details( $booking->order_id );

            if ( empty( $order_details ) ) {
                continue;
            }

            $email = build_pickup_reminder_email( $booking, $order_details, $is_morning );

            $headers = [
                'Content-Type: text/html; charset=UTF-8',
                'From: GNYC Youth Store <store@gnycyouth.org>',
                'Reply-To: GNYC Youth Store <store@gnycyouth.org>',
            ];

            wp_mail(
                $booking->customer_email,
                $email['subject'],
                $email['html'],
                $headers
            );
        }
    }

    delete_transient( $lock_key );
}

/**
 * Cron hook — day before reminder.
 */
add_action( 'send_pickup_day_before_reminders', function() {
    send_pickup_reminders( false );
} );

/**
 * Cron hook — morning of reminder.
 */
add_action( 'send_pickup_morning_reminders', function() {
    send_pickup_reminders( true );
} );