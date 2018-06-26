<?php

namespace app\controllers\student;


use app\controllers\AbstractController;
use app\libraries\Core;

class LateDaysTableController extends AbstractController {
    public function run() {
        $g_id = isset($_REQUEST["g_id"]) ? $_REQUEST["g_id"] : NULL;
        $user_id = $this->core->getUser()->getId();
        $total_late_used = 0;
        $student_gradeables = array();
        $status_array = array();
        $late_charged_array = array();
        $order_by = [
            'CASE WHEN eg.eg_submission_due_date IS NOT NULL THEN eg.eg_submission_due_date ELSE g.g_grade_released_date END'
        ];
        foreach ($this->core->getQueries()->getGradeablesIterator(null, $user_id, 'registration_section', 'u.user_id', 0, $order_by) as $gradeable) {
            $student_gradeables[] = $gradeable;
            $gradeable->calculateLateDays($total_late_used);
            $status_array[] = $gradeable->getLateStatus();
            $late_charged_array[] = $gradeable->getCurrLateCharged();
        }
        $late_update = $this->core->getQueries()->getLateDayUpdates($user_id);
        $preferred_name = $this->core->getQueries()->getUserById($user_id)->getDisplayedFirstName() . " " . $this->core->getQueries()->getUserById($user_id)->getLastName();
        switch ($_REQUEST['action']) {
            case 'plugin_table':
                return $this->core->getOutput()->renderOutput(array('LateDaysTable'), 'showLateTable',
                    $user_id,
                    $g_id,
                    $student_gradeables,
                    $status_array,
                    $late_charged_array,
                    $total_late_used,
                    $late_update,
                    $preferred_name,
                    false);
                break;
            default:
                return $this->core->getOutput()->renderOutput(array('LateDaysTable'), 'showLateTable',
                    $user_id,
                    $g_id,
                    $student_gradeables,
                    $status_array,
                    $late_charged_array,
                    $total_late_used,
                    $late_update,
                    $preferred_name,
                    true);
                break;
        }
    }
}