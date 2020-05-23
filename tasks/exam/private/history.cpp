#include <ncursesw/ncurses.h>
#include <ncursesw/form.h>
#include <locale.h>
#include <unistd.h>
#include <string.h>

const char *flag_enc = "+++flag+++";
char flag[1024];

inline void decode_flag() {
    char c = 0;
    int fl = 0;
    for (int i = 0; flag_enc[i]; ++i) {
        if (flag_enc[i] == '\x7f') {
            flag[fl] = c;
            c = 0;
            ++fl;
        } else {
            c += flag_enc[i];
        }
    }
    flag[fl] = '\0';
}

WINDOW *win, *dw;
FORM *form;
FIELD *fields[2] = {NULL, NULL};

char text[1024];

const char *ANSWERS[] = {
    NULL,
    "Ленин                                                                           ",
    "1812                                                                            ",
    "Месопотамия                                                                     ",
    "26                                                                              ",
    "XVIII                                                                           ",
    "Пятая                                                                           ",
    "Сэр Уинстон Леонард Спенсер-Черчилль                                            ",
    "Федеративная Республика Бразилия                                                ",
    "Покушение                                                                       ",
    "Трудоёмкий процесс планирования не успевал за реальными потребностями населения ",
};

int state = 0;
int correct = 0;

int debug, debug2;

void redraw(bool resize) {
    if (resize) {
        endwin();
        refresh();

        wclear(win);
        wresize(win, LINES-1, COLS-2);
        box(win, 0, 0);
        touchwin(win);

        set_form_win(form, win);
        set_form_sub(form, dw);
    }
    if (state == -1) {
        mvwprintw(win,  4, (COLS-37)/2, "Э К З А М Е Н  п о  И С Т О Р И И"); 
        if (correct == 55 * 40) {
            decode_flag();
            mvwprintw(win,  8, (COLS-80)/2, "Оценка за экзамен — о т л и ч н о !");
            mvwprintw(win, 10, (COLS-80)/2, "Поздравляю. Вы справились с экзаменом, а он был весьма непрост!");
            mvwprintw(win, 11, (COLS-80)/2, "Я горжусь вами. Вы — прекрасный ученик! Обратитесь ко мне после уроков, мы обсудим");
            mvwprintw(win, 12, (COLS-80)/2, "ваше участие в школьной олимпиаде по истории в следующем учебном году.");
            mvwprintw(win, 14, (COLS-80)/2, "Для выставления оценки в журнал и дневник отправьте мне этот код:");
            mvwprintw(win, 15, (COLS-80)/2, flag);
            mvwprintw(win, 17, (COLS-80)/2, " ");
        } else {
            mvwprintw(win,  8, (COLS-80)/2, "Оценка за экзамен — н е у д о в л е т в о р и т е л ь н о.");
            mvwprintw(win, 10, (COLS-80)/2, "Позор! Вы не смогли ответить без ошибок даже на такие элементарные вопросы!");
            mvwprintw(win, 11, (COLS-80)/2, "Ваша успеваемость в этом учебном году под угрозой. Необходим серьёзный разговор");
            mvwprintw(win, 12, (COLS-80)/2, "с привлечением ваших родителей, в первую очередь отца.");
            mvwprintw(win, 14, (COLS-80)/2, "И никакой код вы не заслужили.");
        }
    } else if (state == 0) {
        mvwprintw(win,  4, (COLS-37)/2, "Э К З А М Е Н  п о  И С Т О Р И И"); 
        mvwprintw(win,  8, (COLS-80)/2, "Здравствуй, дорогой ученик! Я, Вениамин Витальевич, придумал эту программу");
        mvwprintw(win,  9, (COLS-80)/2, "специально для вас. Вам предстоит сдать непростой экзамен по моему");
        mvwprintw(win, 10, (COLS-80)/2, "предмету — истории.");
        mvwprintw(win, 12, (COLS-80)/2, "При получении удовлетворительной оценки вы получите код, который вам нужно");
        mvwprintw(win, 13, (COLS-80)/2, "будет передать мне, чтобы получить оценку в журнал и дневник.");
        mvwprintw(win, 15, (COLS-80)/2, "Ж е л а ю   у  д а  ч и !");
        mvwprintw(win, 17, (COLS-80)/2, "Нажмите любую клавишу, чтобы продолжить.");
    } else if (state > 0) {
        mvwprintw(win,  4, (COLS-37)/2, "В О П Р О С      н о м е р      %d", state); 
        mvwprintw(win,  6, (COLS-37)/2, "Нажмите E n t e r, чтобы ответить.");
        if (state == 1) {
            mvwprintw(win, 10, (COLS-80)/2, "Разминка. Кто был раньше — Владимир Ильич ЛЕНИН или Иосиф Виссарионович СТАЛИН?");
        } else if (state == 2) {
            mvwprintw(win, 10, (COLS-80)/2, "Идём дальше. В каком году завершилась ОТЕЧЕСТВЕННАЯ ВОЙНА 1812 года?");
        } else if (state == 3) {
            mvwprintw(win, 10, (COLS-80)/2, "Продолжаем. Какой древний географический регион находился между реками");
            mvwprintw(win, 11, (COLS-80)/2, "ТИГР и ЕВФРАТ?");
        } else if (state == 4) {
            mvwprintw(win, 10, (COLS-80)/2, "Ещё вопрос. Сколько полных лет просуществовала ЛИГА НАЦИЙ?");
        } else if (state == 5) {
            mvwprintw(win, 10, (COLS-80)/2, "И ещё один вопрос. В каком веке в АВСТРАЛИИ была основана первая БРИТАНСКАЯ КОЛОНИЯ?");
        } else if (state == 6) {
            mvwprintw(win, 10, (COLS-80)/2, "Ещё один вопрос. Какая по счёту РЕСПУБЛИКА основана во ФРАНЦИИ в 1958 году?");
        } else if (state == 7) {
            mvwprintw(win, 10, (COLS-80)/2, "Следующий вопрос. Каково полное имя руководителя государства, участвовавшего");
            mvwprintw(win, 11, (COLS-80)/2, "в ЯЛТИНСКОЙ конференции наряду со СТАЛИНЫМ и РУЗВЕЛЬТОМ?");
        } else if (state == 8) {
            mvwprintw(win, 10, (COLS-80)/2, "Продолжим. Как полностью называется современное государство, вторым по численности");
            mvwprintw(win, 11, (COLS-80)/2, "населения городом которого является РИО-ДЕ-ЖАНЕЙРО?");
        } else if (state == 9) {
            mvwprintw(win, 10, (COLS-80)/2, "Далее. Какова была причина смерти российского императора АЛЕКСАНДРА II?");
        } else if (state == 10) {
            mvwprintw(win, 10, (COLS-80)/2, "И последний вопрос. Каков основной недостаток ПЛАНОВОЙ ЭКОНОМИКИ, принятой в СССР?");
        }
    }
    touchwin(win);
    wrefresh(win);
    pos_form_cursor(form);
}

inline void run() {
    wint_t key; int wch_state;

    win = newwin(LINES - 1, COLS - 2, 1, 1);
    dw = derwin(win, 1, 80, 15, (COLS-80)/2);
    keypad(win, 1);

    fields[0] = new_field(1, 80, 0, 0, 0, 0);
    set_field_opts(fields[0], O_VISIBLE | O_PUBLIC | O_EDIT | O_ACTIVE | O_STATIC);
    set_field_back(fields[0], A_STANDOUT);
    set_field_buffer(fields[0], 0, "");
    set_field_pad(fields[0], ' ');

    form = new_form(fields);

    redraw(true);
    while (true) {
        wch_state = wget_wch(win, &key);
        if (key == KEY_RESIZE) {
            redraw(true);
        } else if (state > 0) {
            if (key == KEY_LEFT) {
                form_driver_w(form, KEY_CODE_YES, REQ_PREV_CHAR);
                redraw(false);
            } else if (key == KEY_RIGHT) {
                form_driver_w(form, KEY_CODE_YES, REQ_NEXT_CHAR);
                redraw(false);
            } else if (key == KEY_BACKSPACE || key == 127) {
                form_driver_w(form, KEY_CODE_YES, REQ_DEL_PREV);
                redraw(false);
            } else if (key == KEY_DC) {
                form_driver_w(form, KEY_CODE_YES, REQ_DEL_CHAR);
                redraw(false);
            } else if (key == '\n') {
                form_driver_w(form, KEY_CODE_YES, REQ_END_LINE);
                if (!strncmp(field_buffer(fields[0], 0), ANSWERS[state], 80)) {
                    mvwprintw(win, 22, (COLS-32)/2, "Это  п р а в и л ь н ы й  ответ!");
                    correct += state * 40;
                } else {
                    mvwprintw(win, 22, (COLS-36)/2, "Это  н е п р а в и л ь н ы й  ответ.");
                }
                wrefresh(win);
                sleep(1);

                form_driver_w(form, KEY_CODE_YES, REQ_CLR_FIELD);
                set_field_buffer(fields[0], 0, "");
                ++state;
                if (state == 11) {
                    state = -1;
                }
                unpost_form(form);
                redraw(true);
                if (state > 0) {
                    post_form(form);
                }
                wrefresh(win);
                wrefresh(dw);
            } else {
                form_driver_w(form, wch_state, key);
                redraw(false);
            }
        } else {
            if (state == 0) {
                state = 1;
                redraw(true);
                post_form(form);
                wrefresh(win);
                wrefresh(dw);
            } else {
                redraw(false);
            }
        }
    }

    unpost_form(form);
    free_form(form);
    free_field(fields[0]);
}

int main() {
    setlocale(LC_CTYPE, "C.UTF-8");

    initscr();
    noecho();
    run();
    delwin(win);
    endwin();

    return 0;
}

